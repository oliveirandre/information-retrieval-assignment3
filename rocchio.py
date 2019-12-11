import operator

class Rocchio:
    def __init__(self):
        self.alpha = 1
        self.beta = 0.5
        self.gamma = 0.25
        self.Rocchio = {}
    
    def ChangeValues(self, alpha, beta, gamma):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        return

    
    def RocchioAlgorithm(self, query, results, relevant_docs):
        #print(query)
        relevants = {}
        irrelevants = {}
        f = open("result/big_boy0", "r")
        lines = [line.strip() for line in f.readlines()]
        f.close()
        count = 0

        for res in results:
            if res not in relevant_docs:
                count += 1

        for line in lines:
            for i in range(1, len(line.split(";"))-1):
                post = line.split(";")[0]
                term = post.split(":")[0]
                posting = line.split(";")[i]

                # relevant documents
                if posting.split(":")[0] in relevant_docs and posting.split(":")[0] in results:
                    weight = posting.split(":")[1]
                    if term in relevants:
                        relevants[term] += float(weight)
                    else:
                        relevants[term] = float(weight)
                
                #irrelevant documents
                elif posting.split(":")[0] not in relevant_docs and posting.split(":")[0] in results:
                    weight = posting.split(":")[1]
                    if term in irrelevants:
                        irrelevants[term] += float(weight)
                    else:
                        irrelevants[term] = float(weight)       

        # initialize Rocchio parameters
        beta = self.beta/len(relevant_docs)
        if(count > 0):
            gamma = self.gamma/count
        else:
            gamma = 0

        final = {}
        for t in query:
            final[t] = float(query[t])

        for t in relevants:
            if t in final:
                final[t] += beta*float(relevants[t])
            else:
                final[t] = beta*float(relevants[t])
        
        for t in irrelevants:
            if t in final:
                final[t] -= gamma*float(irrelevants[t])
            else:
                final[t] = gamma*float(irrelevants[t])
        
        return(dict(sorted(final.items(), key=operator.itemgetter(1), reverse=True)[:15]))




    

