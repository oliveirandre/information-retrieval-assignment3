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
path = "queries.txt"

"""
Statistics:
    nº de PMIDs: 4,995,122
    nº de TI's no Doc 1: 2295504
    nº de TI's no Doc 2: 2295504

Notes:
    Tempo não melhora usando High Memory + Threading mode portanto essa opção foi cortada (requeria neste caso 24Gb de RAM)
"""

def main():
    global verbose
    global path

    r = RankedRetriever()

    # Test: PMID- 10605440
    #       TI  - Movement of sea urchin sperm flagella.
    #print(r.query("Isolation and characterization of kinetoplast DNA from bloodstream form of Trypanosoma brucei", 10))

    query_result = {}

    # Correr querie rank para todos
    f = open(path, "r")
    line = "First"
    while True:
        line = f.readline()
        if line == "":
            break
        temp = line.split("\t")
        #print("Query n. " + temp[0] + ": " + temp[1])
        query_result[temp[0]] = r.query(temp[1])
    #print(query_result)

    # Comparar com o query relevance
    # 1 - query mais relevante, 2 - query menos relevante
    query_relevance = {}
    f = open("queries.relevance.txt", "r")
    while True:
        line = f.readline()
        if line == "":
            break
        temp = line.split("\t")
        if temp[0] in query_relevance.keys():
            query_relevance[temp[0]].append((temp[1],temp[2].replace("\n","")))
        else:
            query_relevance[temp[0]] = [(temp[1],temp[2].replace("\n",""))]
    #print(query_relevance["1"])





'''
    Functions to process command line arguments
'''
def readCLArguments(args):
    global verbose
    global path
    if ('--help' in args):
        printHelp()
    if ('-v' in args):
        verbose = True
    if ('--path' in args or '-p' in args):
        path = args[args.index('-p') + 1]





def printHelp():
    print("usage: python3 main.py [option]")
    print("Options:")
    print("-v           : verbose mode")
    sys.exit(1)

if __name__ == "__main__":
    main()
