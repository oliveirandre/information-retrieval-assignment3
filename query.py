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
        # print(recall)
        # print(precision)
        return (sum(a_precision) / len(a_precision), precision[rank-1])
    

    def calcNDCG(self): # TODO: Verificar de acordo com as sugestões do prof
        # relevances = [int(x[1]) if int(x[1]) == 0 else 3 - int(x[1]) for x in self.real] # Cálculo das relevâncias ideiais
        # relevances.sort(reverse=True)
        total = 0
        real_relevances = []
        for i in self.results: # Cálculo das relevâncias atuais
            if i in self.real_wo_weights:
                for x in self.real:
                    if i == x[0]:
                        real_relevances.append(3 - x[1])
            else:
                real_relevances.append(0)
        relevances = sorted(real_relevances, reverse=True)
        ideal = float(relevances[0])
        actual = float(real_relevances[0])
        print(real_relevances)
        print(relevances)
        for i in range(1,len(real_relevances)):
            ideal += float(relevances[i] / math.log(i+1,2))
            actual += float(real_relevances[i] / math.log(i+1,2))
        if ideal == 0:
            return 0
        return actual / ideal
