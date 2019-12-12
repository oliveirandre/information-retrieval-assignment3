from tokenizer import Tokenizer
from indexer import IndexerWeighted
from ltc import TF_IDF_LTC
from rocchio import Rocchio
import math

'''
    TODO:
    1 - Implementar a base

    Extra:
    1 - Tentar implementar uma cache e um método de escolher os blocos a carregar (seja com contadores, etc...)

'''


class RankedRetriever:

    '''
        Passos:
            - Carregar o índice para extrair informação tal como verificação da integridade e o número total de documentos
            -

    '''
    def __init__(self, cache_size = 10):
        # Cache
        self.counters = []
        self.open_indexes = []
        self.index_in_mem = {}
        self.cacheStart(cache_size)

        self.index_marks, self.term_ammount = self.verifyIndex()
        self.r = Rocchio()
        self.relevants = []


    '''
        Passos a fazer:
            - dividir termos da query
            - aplicar o que se aplica no tokenizer
            - calcular os valores como se fosse só um valor de idf
            - fazer o ângulo com todos e ver o top Y
    '''
    def query(self, query, y = 10):
        ltc = TF_IDF_LTC()
        t = Tokenizer()
        tokens = t.tokenize(query)
        i = IndexerWeighted(len(tokens))
        i.addToIndexWeighted("1",tokens,ltc)

        query_weights = {} # Armazenar o tf-idf de cada termo
        doc_weights = {} # Armazenar o tf-idf de cada termo por cada documento (0 se o termo não existir nesse documento)
        #print(self.openTerm("human")["idf"])
        for k in list(i.index.keys()):
            query_weights[k] = i.index[k].split(":")[1]
            #print(query_weights)
            # Retrieve the terms index entry
            term = self.openTerm(k)
            if not term:
                print("Não encontrou o token " + k + " nos indices")
                continue
            
            query_weights[k] = float(query_weights[k]) * float(term['idf'])
            for d in term['docs']:
                if d[0] in doc_weights.keys():
                    # if d[0] == "7551519":
                    #     print(d[1])
                    #print(str(d[1]) + " * " + str(query_weights[k]))
                    doc_weights[d[0]] += float(d[1]) * float(query_weights[k])
                else:
                    doc_weights[d[0]] = float(d[1]) * float(query_weights[k])

        # Return sorted
        sorted_pmids = []
        while len(list(doc_weights.keys())) != 0:
            if(len(sorted_pmids) == y):
                break
            max = (0,0)
            for i in list(doc_weights.keys()):
                if doc_weights[i] > max[1]:
                    max = (i, doc_weights[i])
            sorted_pmids.append(max[0])
            del doc_weights[max[0]]

        if y <= len(sorted_pmids):
            return sorted_pmids[0:y]
        else: # TODO: Meter aqui algoritmo de pesquisar similares
            return sorted_pmids

    def queryWeights(self, query, y = 10):
        ltc = TF_IDF_LTC()
        t = Tokenizer()
        tokens = t.tokenize(query)
        i = IndexerWeighted(len(tokens))
        i.addToIndexWeighted("1",tokens,ltc)

        query_weights = {} # Armazenar o tf-idf de cada termo
        #print(self.openTerm("human")["idf"])
        for k in list(i.index.keys()):
            query_weights[k] = i.index[k].split(":")[1]

        return query_weights

    def expandedQueryResults(self, expanded_query, y = 10):
        query_weights = expanded_query
        doc_weights = {}
        for k in list(query_weights.keys()):
            term = self.openTerm(k)
            if not term:
                print("Não encontrou o token " + k + " nos indices")
                continue
            
            query_weights[k] = float(query_weights[k]) * float(term['idf'])
            for d in term['docs']:
                if d[0] in doc_weights.keys():
                    # if d[0] == "7551519":
                    #     print(d[1])
                    #print(str(d[1]) + " * " + str(query_weights[k]))
                    doc_weights[d[0]] += float(d[1]) * float(query_weights[k])
                else:
                    doc_weights[d[0]] = float(d[1]) * float(query_weights[k])

        # Return sorted
        sorted_pmids = []
        while len(list(doc_weights.keys())) != 0:
            if(len(sorted_pmids) == y):
                break
            max = (0,0)
            for i in list(doc_weights.keys()):
                if doc_weights[i] > max[1]:
                    max = (i, doc_weights[i])
            sorted_pmids.append(max[0])
            del doc_weights[max[0]]

        if y <= len(sorted_pmids):
            return sorted_pmids[0:y]
        else: # TODO: Meter aqui algoritmo de pesquisar similares
            return sorted_pmids


    '''
        Normalization
    '''
    def calculateLength(self, tf_log):
        temp = []
        for i in tf_log:
            temp.append(i**2)
        length = sum(temp)
        length = math.sqrt(length)

        for i in range(len(tf_log)):
            tf_log[i] = tf_log[i]/length
        return tf_log

    '''
        Index verification and access
    '''
    # Abrir o guia do index
    def verifyIndex(self):
        # Abrir o files_index.txt para ver o nº de ficheiros
        f=open("result/files_index.txt", "r")
        lines = f.readlines()
        f.close()
        n = int(lines[-1].split(":")[-1])
        index_marks = {}
        for i in range(len(lines) - 1):
            temp = lines[i].split(":")
            index_marks[temp[1].replace("\n", "")] = int(temp[0])
        print("Found " + str(len(index_marks.keys())) + " index blocks/files.")
        for ci in range(len(index_marks.keys())):
            self.counters.append((ci,0))
        # Abrir ficheiros do indice 1 a 1 para ver o N
        return (index_marks, n)


    '''
    How to simple cache:
        1) Inicializar uma lista de contadores e uma lista de tamanho X
        2) Manter aberto em memoria os ficheiros de indice contidos na lista X
        3) Caso um passe a ser maior, trocar e abrir para memória o novo mais cotado

    '''
    def openTerm(self, term):
        index_file = 0
        for k in self.index_marks.keys():
            if term >= k:
                index_file = self.index_marks[k]
        #print("Term: " + term +" found in document bigboy"  + str(index_file))
        if index_file in self.open_indexes: # Ir buscar à variável que detem este ficheiro em memória
            #print("Fui buscar à cache!")
            for line in self.index_in_mem[index_file]:
                if line[0:len(term)] == term:
                    self.refreshCache(index_file)
                    return self.readFinalIndexLine(line)

        else: # Ir buscar à mão 
            f = open("result/big_boy" + str(index_file), "r")
            line = "Oi"
            while line != "":
                line = f.readline()
                # if term in line
                # if term[0:4] in line
                # if term[0:4] == line[0:4]
                if line[0:len(term)] == term:
                    f.close()
                    self.refreshCache(index_file)
                    return self.readFinalIndexLine(line)


    def refreshCache(self, index_file):
        self.counters[index_file] = (self.counters[index_file][0], self.counters[index_file][1] + 1)
        # Verificar lista de contadores
        sorted_by_count = sorted(self.counters, key=lambda x: x[1])[::-1]
        # Comparar se o top 10 contadores estão abertos
        new = [x[0] for x in sorted_by_count[0:len(self.open_indexes)]]
        current = self.open_indexes

        remove = set(current) - set(new)        # Desta forma só mexemos se for mesmo preciso, 
        introduce = set(new) - set(current)     # não nos obriga a reler tudo.
        for i in remove:
            del self.index_in_mem[i]
        
        for i in new:
            f = open("result/big_boy" + str(i), "r")
            self.index_in_mem[i] = f.readlines()
            f.close()
        self.open_indexes = new # Actualizar os indexes que estão abertos
        #print("Refreshed the cache:" + str(self.open_indexes))

    
    def cacheStart(self, cache_size):
        self.open_indexes = list(range(0,cache_size))
        for i in self.open_indexes:
            #f = open("result/big_boy0", "r")
            f = open("result/big_boy" + str(i), "r")
            self.index_in_mem[i]  = f.readlines()
            f.close()
        


    # Abrir uma linha do índice
    def readFinalIndexLine(self,line):
        temp = line.split(";")
        temp1 = temp[0].split(":")
        term = {}
        term["name"] = temp1[0]
        term["idf"] = temp1[1]
        term["docs"] = []

        for i in range(1,len(temp)-1):
            temp2 = temp[i].split(":")
            term["docs"].append((temp2[0], temp2[1], temp2[2].split(",")))
        return term

    


