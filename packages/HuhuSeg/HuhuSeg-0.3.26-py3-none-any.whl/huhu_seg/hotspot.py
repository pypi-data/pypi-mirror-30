#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import numpy
import math
from .bow import Corpura

class HotSpot :

    def __init__(self, clusters, content_attr) :
        if not isinstance(clusters, collections.Iterable) :
            print('Para corpura should be an iterable object')
            return
        self.flat = lambda L: sum(map(self.flat,L),[]) if isinstance(L,list) else [L]
        self.corpura_inst = Corpura([corpus[content_attr] for corpus in self.flat(clusters)])
        self.clusters = clusters
        self.content_attr = content_attr

    def computing(self) :
        doc_freq = list()
        for cluster in self.clusters :
            doc_freq.append(sum([len(c) for c in cluster]))
        doc_freq_array = numpy.array(doc_freq)
        doc_freq_array = doc_freq_array / numpy.linalg.norm(doc_freq_array)

        self.topics = list()
        for i in range(len(doc_freq)) :
            percent_doc_freq = float(doc_freq[i]) / float(sum(doc_freq))
            total_weights = sum(self.corpura_inst.corpura2average_bow([corpus[self.content_attr] for corpus in self.flat(self.clusters[i])]))
            hotspot = doc_freq_array[i] * math.exp(percent_doc_freq) * math.log(total_weights)
            self.topics.append((self.clusters[i], hotspot))
        self.topics.sort(key = lambda d:d[1], reverse = True)
        return self.topics


