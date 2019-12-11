import math

class QueryStatistics:
    
    results = []
    real = []

    def __init__(self, results, real, size, total, rank):
        self.results = results # lista ordenada com resultados da query 
        self.real = real # lista de tuplos com relevâncias (PMID, RELEVANCIA)
        self.real_wo_weights = [x[0] for x in self.real]
        self.size = size # k
        self.total = total # número de documentos total
        self.precision = self.calcPrecision()
        self.recall = self.calcRecall()
        self.f_measure = self.calcF_measure()
        self.ap, self.mp = self.calcAP(rank)
        self.ndcg = self.calcNDCG()



    def calcPrecision(self):
        tp = 0
        fp = 0
        for i in self.results:
            if i in self.real_wo_weights:
                tp += 1
            else:
                fp += 1
        if tp == 0 and fp == 0:
            return 0
        return tp / (tp + fp)

    def calcRecall(self):
        tp = 0
        fn = 0
        for i in self.real_wo_weights:
            if i in self.results:
                tp += 1
            else:
                fn += 1
        if tp == 0 and fn == 0:
            return 0
        return tp / (tp + fn)
        
    def calcF_measure(self):
        if self.recall == 0 and self.precision == 0:
            return 0
        return (2* self.recall * self.precision) / (self.recall + self.precision)

    def calcAP(self, rank): # TODO: Corrigir, recall não precisa de tender para 1, apenas para o máximo possível
        
        if rank > len(self.results):
            rank = len(self.results)
        relevant_docs = [value for value in self.results if value in self.real_wo_weights]
        recall = []         # Vamos manter estes dois (recall e precision) para depois fazer uns gráficos para o relatório
        precision = [] 
        document_count = 0
        relevant_count = 0
        total_relevant = len(relevant_docs)
        if (total_relevant == 0):
            return (0, 0)
        a_precision = []

        for i in self.results:
            document_count += 1
            if i in self.real_wo_weights:
                relevant_count += 1
                a_precision.append(relevant_count / document_count) 
            recall.append(relevant_count / total_relevant)
            precision.append(relevant_count / document_count)
        print(recall)
        print(precision)
        return (sum(a_precision) / len(a_precision), precision[rank-1])
    

    def calcNDCG(self): # TODO: Verificar de acordo com as sugestões do prof
        relevances = [int(x[1]) if x[1] == 0 else 3 - int(x[1]) for x in self.real]
        relevances.sort()
        ideal = relevances[0]
        actual = self.real[0][1]
        total = 0
        for i in range(1,len(self.real)):
            t_rel = 0
            if self.real[i][1] > 0:
                t_rel = 3 - self.real[i][1]
            ideal += relevances[i] / math.log(i+1,2)
            actual += self.real[i][1] / math.log(i+1,2)
        return ideal/actual
