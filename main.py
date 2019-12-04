# coding: utf-8

"""
Authors:
- André Oliveira, nº79969
- Dinis Canastro, nº80299
"""

import Stemmer
import os
import sys
import time
from indexer import IndexerWeighted
from indexer import Indexer
from tokenizer import Tokenizer
from retriever import RankedRetriever
from lnc import TF_IDF_LNC
from ltc import TF_IDF_LTC
import threading
import gc

verbose = False
threads = False
low_memory = True
compression1 = False
compression2 = False
min_token_size = 3
stemmer_cache = 10000
spimi = False
weight = None
index_mode = "None"

# Parametros que não vão para o CLI porque não suporta todos :,)
read_size = 100000
file_limit = 1000000
reading_window = 1000
split_mode_file_size = 10000


"""
Statistics:
    nº de PMIDs: 4,995,122
    nº de TI's no Doc 1: 2295504
    nº de TI's no Doc 2: 2295504

Notes:
    Tempo não melhora usando High Memory + Threading mode portanto essa opção foi cortada (requeria neste caso 24Gb de RAM)
"""

def main():
    r = RankedRetriever()

    # Test: PMID- 10605440
    #       TI  - Movement of sea urchin sperm flagella.
    r.query("Movement of sea urchin sperm flagella", 10)




'''
    Functions to process command line arguments
'''
def readCLArguments(args):

    if ('--help' in args):
        printHelp()





def printHelp():
    print("usage: python3 main.py [option]")
    print("Options:")
    print("-v           : verbose mode")
    sys.exit(1)

if __name__ == "__main__":
    main()
