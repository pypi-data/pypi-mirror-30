# -*- coding: utf-8 -*-
# cython: profile=False

import joblib
import logging
import multiprocessing
import os
import time
import six
import six.moves.cPickle as pickle
import numpy as np
cimport numpy as np
cimport cython
from cpython cimport array
from collections import defaultdict
from ctypes import c_float, c_int32, c_uint32, c_uint64
from contextlib import closing
from libc.math cimport exp
from libc.stdint cimport int32_t, uint32_t, uint64_t
from libc.stdlib cimport rand, RAND_MAX
from libc.string cimport memset
from marisa_trie import Trie, RecordTrie
from multiprocessing.pool import Pool
from scipy.linalg cimport cython_blas as blas
try:
    import itertools.imap as map  # for Python 2
except ImportError:
    pass

from .dictionary cimport Dictionary, Item, Word, Entity
from .extractor cimport Extractor, Paragraph, WikiLink
from .link_graph cimport LinkGraph
from .utils.wiki_page cimport WikiPage

ctypedef np.float32_t float32_t

DEF MAX_EXP = 6
DEF EXP_TABLE_SIZE = 1000

logger = logging.getLogger(__name__)

cdef Dictionary dictionary
cdef LinkGraph link_graph
cdef float32_t [:, :] syn0
cdef float32_t [:, :] syn1
cdef float32_t [:] work
cdef uint32_t [:] word_neg_table
cdef uint32_t [:] entity_neg_table
cdef float32_t [:] exp_table
cdef uint32_t [:] sample_ints
cdef int32_t [:] link_indices
cdef Extractor extractor
cdef unicode language
cdef object alpha
cdef object word_counter
cdef object link_cursor
cdef uint64_t total_words


cdef class _Parameters:
    cdef public uint32_t dim_size
    cdef public float32_t init_alpha
    cdef public float32_t min_alpha
    cdef public uint32_t window
    cdef public uint32_t negative
    cdef public float32_t word_neg_power
    cdef public float32_t entity_neg_power
    cdef public float32_t sample
    cdef public uint32_t iteration
    cdef public uint32_t links_per_page
    cdef dict _kwargs

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return self._kwargs


cdef _Parameters params


cdef class Wikipedia2Vec:
    cdef Dictionary _dictionary
    cdef list _train_history
    cdef public np.ndarray syn0
    cdef public np.ndarray syn1

    def __init__(self, dictionary):
        self._dictionary = dictionary
        self._train_history = []

    property dictionary:
        def __get__(self):
            return self._dictionary

    property train_history:
        def __get__(self):
            return self._train_history

    cpdef get_word(self, unicode word, default=None):
        return self._dictionary.get_word(word, default)

    cpdef get_entity(self, unicode title, bint resolve_redirect=True, default=None):
        return self._dictionary.get_entity(title, resolve_redirect, default)

    cpdef np.ndarray get_word_vector(self, unicode word):
        cdef Word obj

        obj = self._dictionary.get_word(word)
        if obj is None:
            raise KeyError()
        return self.syn0[obj.index]

    cpdef np.ndarray get_entity_vector(self, unicode title, bint resolve_redirect=True):
        cdef Entity obj

        obj = self._dictionary.get_entity(title, resolve_redirect=resolve_redirect)
        if obj is None:
            raise KeyError()
        return self.syn0[obj.index]

    cpdef np.ndarray get_vector(self, Item item):
        return self.syn0[item.index]

    cpdef list most_similar(self, Item item, count=100):
        cdef np.ndarray vec

        vec = self.get_vector(item)
        return self.most_similar_by_vector(vec, count)

    cpdef list most_similar_by_vector(self, np.ndarray vec, count=100):
        dst = (np.dot(self.syn0, vec) / np.linalg.norm(self.syn0, axis=1) / np.linalg.norm(vec))
        indexes = np.argsort(-dst)

        return [(self._dictionary.get_item_by_index(ind), dst[ind]) for ind in indexes[:count]]

    def init_sims(self):
        for i in xrange(self.syn0.shape[0]):
            self.syn0[i, :] /= np.sqrt((self.syn0[i, :] ** 2).sum(-1))

    def save(self, out_file):
        joblib.dump(dict(
            syn0=self.syn0,
            syn1=self.syn1,
            dictionary=self._dictionary.serialize(),
            train_history=self._train_history
        ), out_file)

    def save_text(self, out_file):
        with open(out_file, 'wb') as f:
            for item in sorted(self.dictionary, key=lambda o: o.doc_count, reverse=True):
                vec_str = ' '.join('%.4f' % v for v in self.get_vector(item))
                if isinstance(item, Word):
                    text = item.text.replace('\t', ' ')
                else:
                    text = 'ENTITY/' + item.title.replace('\t', ' ')

                f.write(('%s\t%s\n' % (text, vec_str)).encode('utf-8'))

    @staticmethod
    def load(in_file, numpy_mmap_mode='c'):
        obj = joblib.load(in_file, mmap_mode=numpy_mmap_mode)
        if isinstance(obj['dictionary'], dict):
            dictionary = Dictionary.load(obj['dictionary'])
        else:
            dictionary = obj['dictionary']  # for backward compatibilit

        ret = Wikipedia2Vec(dictionary)
        ret.syn0 = obj['syn0']
        ret.syn1 = obj['syn1']
        ret._train_history = obj['train_history']

        return ret

    @staticmethod
    def load_text(in_file):
        words = defaultdict(int)
        entities = defaultdict(int)
        vectors = []

        with open(in_file, 'rb') as f:
            for (n, line) in enumerate(f):
                (item_str, vec_str) = line.decode('utf-8').split('\t')
                if item_str.startswith('ENTITY/'):
                    entities[item_str[7:]] = n
                else:
                    words[item_str] = n

                vectors.append(np.array([float(s) for s in vec_str.split(' ')], dtype=np.float32))

        syn0 = np.empty((len(vectors), vectors[0].size))

        word_dict = Trie(words.keys())
        entity_dict = Trie(entities.keys())
        redirect_dict = RecordTrie('<I')

        for (word, ind) in six.iteritems(word_dict):
            syn0[ind] = vectors[words[word]]

        entity_offset = len(word_dict)
        for (title, ind) in six.iteritems(entity_dict):
            syn0[ind + entity_offset] = vectors[entities[title]]

        word_stats = np.zeros((len(word_dict), 2), dtype=np.uint32)
        entity_stats = np.zeros((len(entity_dict), 2), dtype=np.uint32)

        dictionary = Dictionary(word_dict, entity_dict, redirect_dict, word_stats, entity_stats,
                                None, dict())
        ret = Wikipedia2Vec(dictionary)
        ret.syn0 = syn0
        ret.syn1 = None
        ret._train_history = []

        return ret

    def train(self, dump_reader, link_graph_, pool_size, chunk_size, **kwargs):
        global dictionary, link_graph, syn0, syn1, work, word_neg_table, entity_neg_table,\
            exp_table, sample_ints, link_indices, word_counter, link_cursor, extractor, alpha,\
            params, total_words

        start_time = time.time()

        params = _Parameters(**kwargs)

        words = list(self.dictionary.words())
        total_word_cnt = int(sum(w.count for w in words))
        total_words = total_word_cnt * params.iteration
        logger.info('Total number of word occurrence: %d', total_words)

        thresh = params.sample * total_word_cnt

        logger.info('Building a sampling table for frequent words...')

        sample_ints = multiprocessing.RawArray(c_uint32, len(words))
        for word in words:
            cnt = float(word.count)
            if params.sample == 0:
                word_prob = 1.0
            else:
                word_prob = min(1.0, (np.sqrt(cnt / thresh) + 1) * (thresh / cnt))
            sample_ints[word.index] = int(round(word_prob * RAND_MAX))

        logger.info('Building tables for negative sampling...')

        word_neg_table = self._build_word_neg_table(params.word_neg_power)
        entity_neg_table = self._build_entity_neg_table(params.entity_neg_power)

        logger.info('Building tables for link indices...')

        offset = self.dictionary.entity_offset
        indices = np.arange(offset, offset + len(list(self.dictionary.entities())))
        if link_graph_:
            link_indices = multiprocessing.RawArray(c_int32, np.random.permutation(indices))
        else:
            link_indices = None

        link_cursor = multiprocessing.Value(c_uint32, 0)

        logger.info('Starting to train embeddings...')

        def iter_dump_reader():
            for n in range(params.iteration):
                logger.info('Iteration: %d', n)
                for page in dump_reader:
                    yield page

        vocab_size = len(self.dictionary)

        logger.info('Initializing weights...')
        dim_size = params.dim_size
        syn0_shared = multiprocessing.RawArray(c_float, dim_size * vocab_size)
        syn1_shared = multiprocessing.RawArray(c_float, dim_size * vocab_size)

        self.syn0 = np.frombuffer(syn0_shared, dtype=np.float32)
        syn0 = self.syn0 = self.syn0.reshape(vocab_size, dim_size)

        self.syn1 = np.frombuffer(syn1_shared, dtype=np.float32)
        syn1 = self.syn1 = self.syn1.reshape(vocab_size, dim_size)

        self.syn0[:] = (np.random.rand(vocab_size, dim_size) - 0.5) / dim_size
        self.syn1[:] = np.zeros((vocab_size, dim_size))

        dictionary = self.dictionary
        link_graph = link_graph_

        extractor = Extractor(dump_reader.language, dictionary.lowercase, dictionary=dictionary)
        word_counter = multiprocessing.Value(c_uint64, 0)
        alpha = multiprocessing.RawValue(c_float, params.init_alpha)
        work = np.zeros(dim_size, dtype=np.float32)

        exp_table = multiprocessing.RawArray(c_float, EXP_TABLE_SIZE)
        for i in range(EXP_TABLE_SIZE):
            exp_table[i] = <float32_t>exp((i / <float32_t>EXP_TABLE_SIZE * 2 - 1) * MAX_EXP)
            exp_table[i] = <float32_t>(exp_table[i] / (exp_table[i] + 1))

        if pool_size == 1:
            for (n, _) in enumerate(map(train_page, iter_dump_reader())):
                if n % 10000 == 0:
                    prog = float(word_counter.value) / total_words
                    logger.info('Proccessing page #%d progress: %.1f%% alpha: %.3f',
                                n, prog * 100, alpha.value)
        else:
            with closing(Pool(pool_size)) as pool:
                for (n, _) in enumerate(pool.imap_unordered(train_page, iter_dump_reader(),
                                                            chunksize=chunk_size)):
                    if n % 10000 == 0:
                        prog = float(word_counter.value) / total_words
                        logger.info('Proccessing page #%d progress: %.1f%% alpha: %.3f',
                                    n, prog * 100, alpha.value)

            logger.info('Terminated pool workers...')

        train_params = dict(
            dump_file=dump_reader.dump_file,
            train_time=time.time() - start_time,
        )
        train_params.update(params.to_dict())

        if link_graph is not None:
            train_params['link_graph'] = dict(build_params=link_graph.build_params)

        self._train_history.append(train_params)

    def _build_word_neg_table(self, power):
        items = list(self._dictionary.words())
        if power == 0:
            return self._build_uniform_neg_table(items)
        else:
            return self._build_unigram_neg_table(items, power)

    def _build_entity_neg_table(self, power):
        items = list(self._dictionary.entities())
        if power == 0:
            return self._build_uniform_neg_table(items)
        else:
            return self._build_unigram_neg_table(items, power)

    def _build_uniform_neg_table(self, items):
        return multiprocessing.RawArray(c_uint32, [o.index for o in items])

    def _build_unigram_neg_table(self, items, power, table_size=100000000):
        neg_table = multiprocessing.RawArray(c_uint32, table_size)
        items_pow = float(sum([item.count ** power for item in items]))

        index = 0
        cur = items[index].count ** power / items_pow

        for table_index in xrange(table_size):
            neg_table[table_index] = items[index].index
            if float(table_index) / table_size > cur:
                if index < len(items) - 1:
                    index += 1
                cur += items[index].count ** power / items_pow

        return neg_table


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
def train_page(WikiPage page):
    cdef uint32_t i, j, start, end, span_start, span_end, word_count, total_nodes
    cdef int32_t word, word2, entity
    cdef int32_t [:] words
    cdef const int32_t [:] neighbors
    cdef unicode word_str
    cdef list word_list
    cdef WikiLink wiki_link

    cdef float32_t alpha_, p
    alpha_ = alpha.value

    # train using Wikipedia link graph
    if link_graph is not None:
        total_nodes = link_indices.size

        with link_cursor.get_lock():
            start = link_cursor.value
            link_cursor.value = (start + params.links_per_page) % total_nodes

        for i in range(start, start + params.links_per_page):
            entity = link_indices[i % total_nodes]
            neighbors = link_graph.neighbor_indices(entity)
            for j in range(len(neighbors)):
                _train_pair(entity, neighbors[j], alpha_, params.negative, entity_neg_table)
                # _train_pair(neighbors[j], entity, alpha_, params.negative, entity_neg_table)

    # train using Wikipedia words and anchors
    for paragraph in extractor.extract_paragraphs(page):
        word_list = paragraph.words
        words = cython.view.array(shape=(len(word_list),), itemsize=sizeof(int32_t), format='i')
        for (i, word_str) in enumerate(word_list):
            words[i] = dictionary.get_word_index(word_str)
        word_count = 0
        for i in range(len(words)):
            word = words[i]
            if word == -1:
                continue

            word_count += 1

            if sample_ints[word] < rand():
                continue

            start = max(0, i - params.window)
            end = min(len(words), i + params.window + 1)
            for j in range(start, end):
                word2 = words[j]

                if word2 == -1 or i == j:
                    continue

                if sample_ints[word2] < rand():
                    continue

                _train_pair(word, word2, alpha_, params.negative, word_neg_table)

        # train using word-entity co-occurrences
        for wiki_link in paragraph.wiki_links:
            entity = dictionary.get_entity_index(wiki_link.title)
            if entity == -1:
                continue

            (span_start, span_end) = wiki_link.span

            start = max(0, span_start - params.window)
            end = min(len(words), span_end + params.window)
            for j in range(start, end):
                word2 = words[j]
                if word2 == -1 or span_start <= j < span_end:
                    continue

                if sample_ints[word2] < rand():
                    continue

                _train_pair(entity, word2, alpha_, params.negative, word_neg_table)
                # _train_pair(word2, entity, alpha_, params.negative, word_neg_table)

        with word_counter.get_lock():
            word_counter.value += word_count  # lock is required since += is not an atomic operation
            p = 1.0 - float(word_counter.value) / total_words
            alpha.value = max(params.min_alpha, params.init_alpha * p)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
@cython.cdivision(True)
cdef inline void _train_pair(int32_t index1, int32_t index2, float32_t alpha, uint32_t negative,
                             uint32_t [:] neg_table) nogil:
    cdef float32_t label, f, g, f_dot
    cdef int32_t index, neg_index
    cdef uint32_t d

    cdef int one = 1
    cdef int dim_size = params.dim_size
    cdef float32_t onef = <float32_t>1.0
    cdef int32_t neg_table_size = len(neg_table)

    memset(&work[0], 0, dim_size * cython.sizeof(float32_t))

    for d in range(negative + 1):
        if d == 0:
            index = index2
            label = 1.0
        else:
            neg_index = rand() % neg_table_size
            index = neg_table[neg_index]
            if index == index2:
                continue
            label = 0.0

        f_dot = <float32_t>(blas.sdot(&dim_size, &syn0[index1, 0], &one, &syn1[index, 0], &one))
        if f_dot >= MAX_EXP or f_dot <= -MAX_EXP:
            continue
        f = exp_table[<int>((f_dot + MAX_EXP) * (EXP_TABLE_SIZE / MAX_EXP / 2))]
        g = (label - f) * alpha

        blas.saxpy(&dim_size, &g, &syn1[index, 0], &one, &work[0], &one)
        blas.saxpy(&dim_size, &g, &syn0[index1, 0], &one, &syn1[index, 0], &one)

    blas.saxpy(&dim_size, &onef, &work[0], &one, &syn0[index1, 0], &one)
