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

    
    def RocchioAlgorithm(self, query, docs):
        relevants = {}
        irrelevants = {}
        f = open("result/big_boy0", "r")
        lines = [line.strip() for line in f.readlines()]
        f.close()
        for line in lines:
            for i in range(1, len(line.split(";"))-1):
                post = line.split(";")[0]
                term = post.split(":")[0]
                posting = line.split(";")[i]

                # relevant documents
                if posting.split(":")[0] in docs:
                    weight = posting.split(":")[1]
                    if term in relevants:
                        relevants[term] += float(weight)
                    else:
                        relevants[term] = float(weight)
                
                #irrelevant documents
                else:
                    weight = posting.split(":")[1]
                    if term in irrelevants:
                        irrelevants[term] += float(weight)
                    else:
                        irrelevants[term] = float(weight)       

        # initialize Rocchio parameters
        alpha = self.alpha
        beta = self.beta
        gamma = self.gamma

        final = {}
        for t in query:
            final[t] = query[t]

        for t in relevants:
            if t in final:
                final[t] += beta*relevants[t]
            else:
                final[t] = beta*relevants[t]

        for t in irrelevants:
            if t in final:
                final[t] -= gamma*irrelevants[t]
            else:
                final[t] = gamma*irrelevants[t]

        for t in query:
            if float(final[t]) < 0:
                final[t] = 0
            
        return final




    

