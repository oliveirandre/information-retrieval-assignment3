from tokenizer import Tokenizer
from indexer import IndexerWeighted
from ltc import TF_IDF_LTC
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
    def __init__(self):
        self.index_marks, self.term_ammount = self.verifyIndex()



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
        #print(i.index)

        query_weights = {} # Armazenar o tf-idf de cada termo
        doc_weights = {} # Armazenar o tf-idf de cada termo por cada documento (0 se o termo não existir nesse documento)
        for k in list(i.index.keys()):
            query_weights[k] = i.index[k].split(":")[1]

            # Retrieve the terms index entry
            term = self.openTerm(k)
            if not term:
                continue

            #print(term)
            for d in term['docs']:
                if d[0] in doc_weights.keys():
                    doc_weights[d[0]] += float(d[1]) * float(query_weights[k])
                else:
                    doc_weights[d[0]] = float(d[1]) * float(query_weights[k])

        # TODO: Get a way to get more values by similarity
        # TODO: Way to cache and retrieve blocks as needed in multi-block environments

        # Return sorted
        sorted_pmids = []
        while len(list(doc_weights.keys())) != 0:
            max = (0,0)
            for i in list(doc_weights.keys()):
                if doc_weights[i] > max[1]:
                    max = (i, doc_weights[i])
            sorted_pmids.append(max[0])
            del doc_weights[max[0]]

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
        print("Found " + str(n) + " terms.")
        # Abrir ficheiros do indice 1 a 1 para ver o N
        print(index_marks)
        return (index_marks, n)


    # TODO: Ler um bloco do index para memória
    def openTerm(self, term):
        index_file = 0
        for k in self.index_marks.keys():
            if term >= k:
                index_file = self.index_marks[k]
                #print("Term: " + term +" found in document bigboy"  + str(index_file))
        f = open("result/big_boy" + str(index_file), "r")
        line = "Oi"
        while line != "":
            line = f.readline()
            if line[0:len(term)] == term:
                return self.readFinalIndexLine(line)


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

    # TODO: Deprecate isto
    # Pesquisar e abrir um unico termo do indice
    def readIndexLineWeights(self,line):
        pass
