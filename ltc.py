# coding: utf-8

"""
Authors:
- André Oliveira, nº79969
- Dinis Canastro, nº80299
"""

import math 

class TF_IDF_LTC:

    def __init__(self):
        self.idf = {}

    # method that calculates the term frequency (1+log(tf))
    def termFrequency(self, terms):
        weighted = {}
        for key in terms:
            weighted[key] = 1 + math.log10(terms[key])
        return weighted    

    # method that normalizes the document terms (log(N/df))
    def normalize(self, tf):
        sum = 0
        normalized = {}
        for key in tf:
            sum += tf[key]
        for key in tf:
            normalized[key] = tf[key] / sum
        return normalized

    # method that calculates the term weights according to the number of documents in the corpus
    def docFrequencyTerm(self, df, n):
        # df - número de documentos em que aparece termo
        # idf - idf = log 10 (N/df)
        return math.log10(n/df)