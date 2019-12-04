# coding: utf-8
import sys
import os

"""
Authors:
- André Oliveira, nº79969
- Dinis Canastro, nº80299
"""

from tokenizer import Tokenizer
import operator
from lnc import TF_IDF_LNC

class IndexerWeighted:
    def __init__(self, word_limit = 100000):
        self.index = {}
        self.documentTerms = {}
        self.df = {}
        self.limit = word_limit
        self.block_count = 0
        self.word_count = 0
        self.finalblocks_count = 0
        self.ensure_dir("/tmp")
        self.ensure_dir("/result")
        #self.big = open("result/big_boy", "w+")
        self.file_index = {}
        self.file_line = 0
        self.final_file_count = 0

    '''
    Optimized indexer:
        Since we use a pair PMID and TI we can consider there will be no further processing on the same document (same PMID).
        As such we skip the verifying if each term has already an entry with such PMID.
        This allowed us to improve a lot on the index creation.
    '''
    def addToIndex(self,docid, values):
        temp_index = {}
        count = 0
        for v in values:
            if v in temp_index:
                temp_index[v][1] += 1
            else:
                temp_index[v] = [docid,1]
        #Dar append/criar ao index geral
        for i in temp_index:
            if i in self.index:
                self.index[i].append(temp_index[i])
            else:
                self.index[i] = [temp_index[i]]
        return

    def clearCurrentIndex(self):
        self.index = {}

    '''
    Method that weights the terms in a document and adds them
    to the index.
    '''
    # criar um index temporário para um documento:
    #   - map em que: key -> term // value -> posição no documento
    #   - calcular pesos dos termos
    #   - posteriormente adicionar ao index geral

    def addToIndexWeighted(self, docid, values, weighting):
        # Lista das posições dos termos num documento
        termsList = {}
        i = 0
        for v in values:
            if v in termsList:
                termsList[v].append(i)
            else:
                termsList[v] = [i]
            i += 1

        df = {}
        for key in termsList:
            df[key] = len(termsList[key])

        tf = weighting.termFrequency(df)
        ntf = weighting.normalize(tf)

        for key in ntf:
            self.addTermToIndex(key, docid, ntf[key], termsList[key])

    def addTermToIndex(self, term, docid, weight, positions):
        if term not in self.index:
            self.index[term] = docid + ":" + str(weight) + ":" + self.listToString(positions) + ";"
        else:
            self.index[term] += docid + ":" + str(weight) + ":" + self.listToString(positions) + ";"

    def listToString(self, l):
        s = ""
        for i in l:
            s += str(i) + ","
        s = s[:-1]
        return s

    '''
    Deprecated
    '''
    # Sending the reference to the instance so it doesn't require context changes every single pair.
    def addAll(self, all, t):
        count = 0
        size = len(all)
        while all:
            count += 1
            if (count % 25000 == 0): print("%.2f" % (count / size * 100))
            tmp = all.pop()
            self.addToIndex(tmp[0], t.tokenize(tmp[1], 3))

    '''
    Method that takes a file_name as input, where the inverse index is written to.
    '''
    # term:idf;doc_id:term_weight;doc_id:term_weight
    def writeToFile(self, file_name):
        f = open(file_name, "w+")
        # Writes in file the sorted index (i.e. the inverse index)
        for key in sorted(self.index.keys()):
            f.write(str(key) + ":")
            for value in self.index[key]:
                f.write(str(value))
            f.write("\n")
        f.close()

    def printIndex(self):
        for i in sorted(self.index.keys()):
            print(i + ":" + str(self.index[i]))

    def ensure_dir(self, file_path):
        if not os.path.exists(os.getcwd() + file_path):
            os.makedirs(os.getcwd() + file_path)

    '''
        Block indexer creation
    '''
    def blockIndexer(self, docid, values, weight = None):
        if weight == None:
            self.addToIndex(docid, values)
        else:
            self.addToIndexWeighted(docid, values, weight)
        self.word_count += len(values)
        if self.word_count >= self.limit:
            self.writeToFile("tmp/block_" + str(self.block_count))
            self.clearCurrentIndex()
            self.word_count = 0
            self.block_count += 1

    '''
        Block merger
    '''
    def mergeBlocks(self, block_size = 100, split = "None", split_size = 100, weight = None, n=0):
        if block_size > self.limit:
            print("[ERROR] BLOCK SIZE MUST BE SMALLER THAN THE AMMOUNT OF WORDS PER FILE")
            sys.exit(0)
        done = False
        # Abrir os ficheiros todos e ir buscar a primeira fila de cada um
        fl = []
        # TL pode ser lido vários blocos de texto raw
        tl = []
        # Processed_TL é apenas um valor processado para dicionário
        processed_tl = []
        for i in range(self.block_count):
            fl.append(open("tmp/block_" + str(i), "r"))
            # Primeira vez que enche
            tl.append([])
            for b in range(block_size):
                tmp = fl[i].readline()
                if tmp != "":
                    tl[i].append(tmp)
                else:
                    #print("APANHEI UM VAZIO")
                    break
            #tl.append([fl[i].readline()]) # WORKING
            processed_tl.append(None)
        #print(len(tl[0]))
        # Loop
        while not done:
            # Processar todos de texto para lista de dicionários, caso esteja vazio vai buscar à tl
            # Re-encher os que foram limpos na ultima iteração
            for t in range(len(tl)):
                if (processed_tl[t]) == None and (len(tl[t]) != 0):
                    processed_tl[t] = self.readIndexLineWeights(tl[t].pop(0))
            # Ver a ordem
            term_list = []
            term_comparison = [] # Não gosto muito disto mas funfa
            for i in processed_tl:
                if i != None:
                    term_list.append(list(i.keys())[0])
                    term_comparison.append(list(i.keys())[0])
                else:
                    term_list.append(None)
            top_term = sorted(term_comparison)[0]

            # Estes indices serão apagados
            indices = [i for i, x in enumerate(term_list) if x == top_term]


            terms = {}
            #print("Termo: " + top_term + " Indices: " + str(indices) + "\nLista:" + str(processed_tl))
            for i in indices:
                if top_term in terms:
                    terms[top_term] += processed_tl[i][top_term]
                else:
                    terms[top_term] = processed_tl[i][top_term]
                # Apagar os indices da lista
                processed_tl[i] = None

            if(weight != None):
                idf = weight.docFrequencyTerm(len(terms[top_term]), n)

            # Escrever no ficheiro
            if split == "None":
                self.writeToFileBlock(terms, idf)
            elif split == "Files":
                self.writeToFiles(terms, split_size, idf)
            elif split == "Index":
                self.writeToFileIndex(terms, idf)
            self.file_line += 1

            # Caso tl tenha slots vazios, encher
            for i in range(len(tl)):
                if len(tl[i]) == 0:
                    for b in range(block_size):
                        temp = fl[i].readline()
                        if temp != "":
                            tl[i].append(temp)
                        else:
                            break
            #print(len(tl[1])) # Control the stack size
            # Verify if all the queues are empty
            done = True
            for i in tl:
                if len(i) != 0:
                    done = False
            #print(processed_tl)

            # TODO: Chegando a um limite passar para o próximo ficheiro
    '''
        Auxiliary method to write to a single file
    '''
    def writeToFileBlock(self,dic, idf):
        key = list(dic.keys())[0]
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(str(idf) + ":" + self.listToString(value))
        self.big.write("\n")

    '''
        Auxiliary method to write to a single file with an index
    '''
    def writeToFileIndex(self,dic, idf):
        key = list(dic.keys())[0]
        if not key[0] in self.file_index.keys():
            if self.file_line != 0:
                self.file_index[key[0]] = self.file_line
                f=open("result/file_index.txt", "a")
                f.write(key[0] + ":" + str(self.file_line + 1) +"\n")
                f.close()
            else:
                self.file_index[key[0]] = self.file_line
                f=open("result/file_index.txt", "w+")
                f.write(key[0] + ":" + str(self.file_line + 1) +"\n")
                f.close()
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(str(idf) + ":" + self.listToString(value))
        self.big.write("\n")

    '''
        Auxiliary method to write to multiple files
    '''
    def writeToFiles(self,dic, s, idf):
        # Se for igual ao limite despoletar a troca de ficheiro
        # Escrever o primeiro valor do ficheiro e o ultimo no índice
        if(self.file_line == s):
            self.big.close()
            self.final_file_count += 1
            self.big = open("result/big_boy" + str(self.final_file_count), "w+")
            self.file_line = 0
        key = list(dic.keys())[0]
        if(self.file_line == 0):
            if self.final_file_count != 0:
                f=open("result/files_index.txt", "a")
                f.write(str(self.final_file_count) + ":" + key +"\n")
                f.close()
            else:
                f=open("result/files_index.txt", "w+")
                f.write(str(self.final_file_count) + ":" + key +"\n")
                f.close()
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(str(idf) + ":" + self.listToString(value))
        self.big.write("\n")


    '''
        Auxiliary method to read index written line
    '''
    def readIndexLine(self,line):
        temp = line.split(":")
        term = temp[0]
        temp_values = temp[1]
        values = []
        index_line = {}
        for i in temp_values.split(";"):
                if not "" in i or not '\n' in i:
                    values.append(i.split(","))
        index_line[term] = values
        return(index_line)

    '''
        Auxiliary method to read index written line with weights
    '''
    def readIndexLineWeights(self,line):
        temp = line.split(":")
        term = temp[0]
        line = line[len(term)+1:]
        #print(line)
        temp_values = line.split(";")

        values = []
        index_line = {}
        for i in temp_values:
                if not "" in i or not '\n' in i:
                    values.append(i.split(","))
        index_line[term] = values
        return(index_line)

class Indexer:
    def __init__(self, word_limit = 10000):
        self.index = {}
        self.documentTerms = {}
        self.df = {}
        self.limit = word_limit
        self.block_count = 0
        self.word_count = 0
        self.finalblocks_count = 0
        self.ensure_dir("/tmp")
        self.ensure_dir("/result")
        self.big = open("result/big_boy", "w+")
        self.file_index = {}
        self.file_line = 0
        self.final_file_count = 0

    '''
    Optimized indexer:
        Since we use a pair PMID and TI we can consider there will be no further processing on the same document (same PMID).
        As such we skip the verifying if each term has already an entry with such PMID.
        This allowed us to improve a lot on the index creation.
    '''
    def addToIndex(self,docid, values):
        temp_index = {}
        count = 0
        for v in values:
            if v in temp_index:
                temp_index[v][1] += 1
            else:
                temp_index[v] = [docid,1]
        #Dar append/criar ao index geral
        for i in temp_index:
            if i in self.index:
                self.index[i].append(temp_index[i])
            else:
                self.index[i] = [temp_index[i]]
        return

    def clearCurrentIndex(self):
        self.index = {}


    def addTermToIndex(self, term, docid, weight, positions):
        if term not in self.index:
            self.index[term] = "" + docid + ":" + str(weight) + ":" + str(positions) + ";"

    '''
    Deprecated
    '''
    # Sending the reference to the instance so it doesn't require context changes every single pair.
    def addAll(self, all, t):
        count = 0
        size = len(all)
        while all:
            count += 1
            if (count % 25000 == 0): print("%.2f" % (count / size * 100))
            tmp = all.pop()
            self.addToIndex(tmp[0], t.tokenize(tmp[1], 3))

    '''
    Method that takes a file_name as input, where the inverse index is written to.
    '''
    # term:idf;doc_id:term_weight;doc_id:term_weight
    def writeToFile(self, file_name):
        f = open(file_name, "w+")
        # Writes in file the sorted index (i.e. the inverse index)
        for key in sorted(self.index.keys()):
            f.write(str(key) + ":")
            for value in self.index[key]:
                f.write(value[0] + "," + str(value[1]) + ";")
            f.write("\n")
        f.close()

    def printIndex(self):
        for i in sorted(self.index.keys()):
            print(i + ":" + str(self.index[i]))

    def ensure_dir(self, file_path):
        if not os.path.exists(os.getcwd() + file_path):
            os.makedirs(os.getcwd() + file_path)


    '''
        Block indexer creation
    '''
    def blockIndexer(self, docid, values):
        self.addToIndex(docid, values)
        self.word_count += len(values)
        if self.word_count >= self.limit:
            self.writeToFile("tmp/block_" + str(self.block_count))
            self.clearCurrentIndex()
            self.word_count = 0
            self.block_count += 1

    '''
        Block merger
    '''
    def mergeBlocks(self, block_size = 1, split = "Files", split_size = 100):
        if block_size > self.limit:
            print("[ERROR] BLOCK SIZE MUST BE SMALLER THAN THE AMMOUNT OF WORDS PER FILE")
            sys.exit(0)
        done = False
        # Abrir os ficheiros todos e ir buscar a primeira fila de cada um
        fl = []
        # TL pode ser lido vários blocos de texto raw
        tl = []
        # Processed_TL é apenas um valor processado para dicionário
        processed_tl = []
        for i in range(self.block_count):
            fl.append(open("tmp/block_" + str(i), "r"))
            # Primeira vez que enche
            tl.append([])
            for b in range(block_size):
                tmp = fl[i].readline()
                if tmp != "":
                    tl[i].append(tmp)
                else:
                    #print("APANHEI UM VAZIO")
                    break
            #tl.append([fl[i].readline()]) # WORKING
            processed_tl.append(None)
        #print(len(tl[0]))
        # Loop
        while not done:
            # Processar todos de texto para lista de dicionários, caso esteja vazio vai buscar à tl
            # Re-encher os que foram limpos na ultima iteração
            for t in range(len(tl)):
                if (processed_tl[t]) == None and (len(tl[t]) != 0):
                    processed_tl[t] = self.readIndexLine(tl[t].pop(0))
            # Ver a ordem
            term_list = []
            term_comparison = [] # Não gosto muito disto mas funfa
            for i in processed_tl:
                if i != None:
                    term_list.append(list(i.keys())[0])
                    term_comparison.append(list(i.keys())[0])
                else:
                    term_list.append(None)
            top_term = sorted(term_comparison)[0]

            # Estes indices serão apagados
            indices = [i for i, x in enumerate(term_list) if x == top_term]


            terms = {}
            #print("Termo: " + top_term + " Indices: " + str(indices) + "\nLista:" + str(processed_tl))
            for i in indices:
                if top_term in terms:
                    terms[top_term] += processed_tl[i][top_term]
                else:
                    terms[top_term] = processed_tl[i][top_term]
                # Apagar os indices da lista
                processed_tl[i] = None

            # Escrever no ficheiro
            if split == "None":
                self.writeToFileBlock(terms)
            elif split == "Files":
                self.writeToFiles(terms, split_size)
            elif split == "Index":
                self.writeToFileIndex(terms)
            self.file_line += 1

            # Caso tl tenha slots vazios, encher
            for i in range(len(tl)):
                if len(tl[i]) == 0:
                    for b in range(block_size):
                        temp = fl[i].readline()
                        if temp != "":
                            tl[i].append(temp)
                        else:
                            break
            #print(len(tl[1])) # Control the stack size
            done = True
            for i in tl:
                if len(i) != 0:
                    done = False
            #print(processed_tl)

            # TODO: Chegando a um limite passar para o próximo ficheiro
    '''
        Auxiliary method to write to a single file
    '''
    def writeToFileBlock(self,dic):
        key = list(dic.keys())[0]
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(value[0] + "," + str(value[1]) + ";")
        self.big.write("\n")

    '''
        Auxiliary method to write to a single file with an index
    '''
    def writeToFileIndex(self,dic):
        key = list(dic.keys())[0]
        if not key[0] in self.file_index.keys():
            if self.file_line != 0:
                self.file_index[key[0]] = self.file_line
                f=open("result/file_index.txt", "a")
                f.write(key[0] + ":" + str(self.file_line + 1) +"\n")
                f.close()
            else:
                self.file_index[key[0]] = self.file_line
                f=open("result/file_index.txt", "w+")
                f.write(key[0] + ":" + str(self.file_line + 1) +"\n")
                f.close()
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(value[0] + "," + str(value[1]) + ";")
        self.big.write("\n")

    '''
        Auxiliary method to write to multiple files
    '''
    def writeToFiles(self,dic, s):
        # Se for igual ao limite despoletar a troca de ficheiro
        # Escrever o primeiro valor do ficheiro e o ultimo no índice
        if(self.file_line == s):
            self.big.close()
            self.final_file_count += 1
            self.big = open("result/big_boy" + str(self.final_file_count), "w+")
            self.file_line = 0
        key = list(dic.keys())[0]
        if(self.file_line == 0):
            if self.final_file_count != 0:
                f=open("result/files_index.txt", "a")
                f.write(str(self.final_file_count) + ":" + key +"\n")
                f.close()
            else:
                f=open("result/files_index.txt", "w+")
                f.write(str(self.final_file_count) + ":" + key +"\n")
                f.close()
        self.big.write(str(key) + ":")
        for value in dic[key]:
            self.big.write(value[0] + "," + str(value[1]) + ";")
        self.big.write("\n")


    '''
        Auxiliary method to read index written line
    '''
    def readIndexLine(self,line):
        temp = line.split(":")
        term = temp[0]
        temp_values = temp[1]
        values = []
        index_line = {}
        for i in temp_values.split(";"):
                if not "" in i or not '\n' in i:
                    values.append(i.split(","))
        index_line[term] = values
        return(index_line)

    '''
    Compression: methods take file_name as input, on which the compressed index is written to.
    Two modes: one with and one without blocking.
    '''
    def dictionaryAsString(self, file_name):
        f = open(file_name, "w")
        s = ""
        d = {}
        i = 0
        for key in sorted(self.index.keys()):
            s += key
        f.write(s)
        f.write("\n")
        for key in sorted(self.index.keys()):
            d[i] = self.index[key]
            f.write(str(i) + ":")
            for value in d[i]:
                f.write(value[0] + "," + str(value[1]) + ";")
            f.write("\n")
            i = i + len(key)

    def blocking(self, file_name):
        f = open(file_name, "w")
        s = ""
        d = {}
        for key in sorted(self.index.keys()):
            s += str(len(key)) + key
        f.write(s)
        f.write("\n")
        for key in sorted(self.index.keys()):
            i = len(key)
            d[i] = self.index[key]
            f.write(str(i) + ":")
            for value in d[i]:
                f.write(value[0] + "," + str(value[1]) + ";")
            f.write("\n")
