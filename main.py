# coding: utf-8

"""
Authors:
- André Oliveira, nº79969
- Dinis Canastro, nº80299

    TODO Extras:
    - Get a way to get more values by similarity
    - Way to cache and retrieve blocks as needed in multi-block environments

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
from query import QueryStatistics
import statistics
from rocchio import Rocchio

verbose = False
path = "queries.txt"
size = 10

def main():
    global verbose
    global path
    global size

    rocchio = Rocchio()
    t = Tokenizer()
    r = RankedRetriever()
    query_result = {}

    # Getting the total list of documents
    f = open("result/files_index.txt")
    n = f.readlines()[-1]

    # '''
    #     10605436
    #     Concerning the localization localization of steroids in centrioles and basal bodies by
    #   immunofluorescence.
    # '''
    # result = r.query("Concerning the localization localization of steroids in centrioles and basal bodies by immunofluorescence.")
    # print(result)

    
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
            query_relevance[temp[0]].append((temp[1],int(temp[2].replace("\n",""))))
        else:
            query_relevance[temp[0]] = [(temp[1],int(temp[2].replace("\n","")))]
    
    relevantdocs = {}
    for key in query_relevance.keys():
        relevantdocs[key] = [x[0] for x in query_relevance[key]]

    # Correr querie rank para todos
    times = []
    f = open(path, "r")
    line = "First"
    while True:
        line = f.readline()
        if line == "":
            break
        temp = line.split("\t")
        #print("Query n. " + temp[0] + ": " + temp[1])
        start_time = time.time()

        query_result[temp[0]] = r.query(temp[1],size)
        
        print("Finished query " + temp[0])
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        #break # Comentar ou não caso se queira fazer só o primeiro
    avg_query_throughput = float(len(times)) / sum(times)
    print("Query throughput: " + str(avg_query_throughput) + " queries/s")
    print("Median Query Latency: " + str(statistics.median(times)) + " s")
    
    results = []
    for i in query_result.keys():
        results.append(QueryStatistics(query_result[i], query_relevance[i], size,n, 10))
    
    '''
    print("Average Precision: " + str(sum([r.precision for r in results]) / len(results)))
    print("Average Recall: "+ str(sum([r.recall for r in results]) / len(results)))
    print("Average F-Measure: "+ str(sum([r.f_measure for r in results]) / len(results)))
    print("Mean Average Precision: "+ str(sum([r.ap for r in results]) / len(results)))
    print("Average Precision at Rank 10: "+ str(sum([r.mp for r in results]) / len(results)))
    print("Average Normalized DCG: "+ str(sum([r.ndcg for r in results]) / len(results)))
    '''

    query_expanded_result = {}
    f = open(path, "r")
    i = 0
    while(True):
        line = f.readline()
        if line == "":
            break
        temp = line.split("\t")
        query_weights = r.queryWeights(temp[1])
        expanded_query = rocchio.RocchioAlgorithm(query_weights, query_result[temp[0]], relevantdocs[temp[0]])
        query_expanded_result[temp[0]] = r.expandedQueryResults(expanded_query, size)
        #break # Comentar ou não caso se queira fazer só o primeiro

    expanded_results = []
    for i in query_expanded_result.keys():
        expanded_results.append(QueryStatistics(query_expanded_result[i], query_relevance[i], size,n, 10))

    k = list(query_expanded_result.keys())[0]
    t = QueryStatistics(query_expanded_result[k], query_relevance[k], size,n, 10)
    print("Precision: " + str(t.precision))
    print("Recall: " + str(t.recall))
    
    print("Average Precision: " + str(sum([r.precision for r in expanded_results]) / len(expanded_results)))
    print("Average Recall: "+ str(sum([r.recall for r in expanded_results]) / len(expanded_results)))
    print("Average F-Measure: "+ str(sum([r.f_measure for r in expanded_results]) / len(expanded_results)))
    print("Mean Average Precision: "+ str(sum([r.ap for r in expanded_results]) / len(expanded_results)))
    print("Average Precision at Rank 10: "+ str(sum([r.mp for r in expanded_results]) / len(expanded_results)))
    print("Average Normalized DCG: "+ str(sum([r.ndcg for r in expanded_results]) / len(expanded_results)))


'''
    Functions to process command line arguments
'''
def readCLArguments(args):
    global verbose
    global path
    global size

    if ('--help' in args):
        printHelp()
    if ('-v' in args):
        verbose = True
    if ('--path' in args):
        path = args[args.index('--path') + 1]
    if ('-s' in args):
        size = int(args[args.index('-s') + 1])





def printHelp():
    print("usage: python3 main.py [option]")
    print("Options:")
    print("-v           : verbose mode")
    print("--path       : Path to the file containing queries")
    print("-s           : Intended size for the resulting queries")
    sys.exit(1)

if __name__ == "__main__":
    main()
