class Rocchio:
    def __init__(self):
        self.alpha = 1
        self.beta = 0.75
        self.gamma = 0.15
        self.WholeS = {}
        self.WeightV = {}
        self.Rocchio = {}
    
    def ChangeValues(self, alpha, beta, gamma):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        return

    def RocchioAlgorithm(self, relevances):
        '''        
        for t in query:
            if t in self.WholeS:
                continue
            else:
                self.WholeS.append(t)
                for i in range(len(self.WeightV)):
                    self.WeightV[i][t] = 0

        nrd = 0 # number of relevant documents
        nid = 0 # number of irrelevant documents

        # update values of nrd and nid
        # alterar para o nosso caso
        for i in range(len(documents)):
            if documents[i] == 1:
                nrd += 1
            else:
                nid += 1
        
        # initialize Rocchio parameters
        alpha = self.alpha
        if nrd > 0:
            beta = self.beta / nrd
        else:
            beta = 0
        if nid > 0:
            gamma = self.gamma / nid
        else:
            gamma = 0

        # build initial query vector
        
        sum = 0
        for t in self.WholeS:
            if t in query:
                self.Rocchio[t] = 1
                sum += 1
            else:
                self.Rocchio[t] = 0
        sum = math.sqrt(sum)
        for t in self.WholeS:
            self.Rocchio[t] /= sum
        '''

        # algorithm
        '''
        for t in self.WholeS:
            self.Rocchio[t] *= alpha
            for i in range(len(documents)):
                if documents[i] == 1:
                    self.Rocchio[t] += beta*self.WeightV[i][t]
                else:
                    self.Rocchio[t] -= gamma*self.WeightV[i][t]
        '''
        print(relevances)


        return




    

