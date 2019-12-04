import Stemmer

"""
Authors:
- André Oliveira, nº79969
- Dinis Canastro, nº80299
"""

class Tokenizer:
    def __init__(self, cache_size = 10000, min_token_size=3):
        self.min_token_size = min_token_size
        self.stemmer = Stemmer.Stemmer('english')
        self.stemmer.maxCacheSize = cache_size # Default value, can be changed
        f = open("snowball_stopwords_EN.txt", "r")
        s = f.read()
        self.stopwords =  s.split("\n")
        self.denied_chars = "+*!\"#$%&/()=?'|\\,;.:-_<>{}[]"

    '''
        Tokenizer complete
    '''
    def tokenize(self, line):
        # Removing denied chars (see them all above)
        for c in self.denied_chars:
            line = line.replace(c, " ")
        # Removing small tokens
        line = ' '.join(word for word in line.split() if len(word)>self.min_token_size)
        # Spliting and lowering case all the tokens
        line = line.lower().split(" ")
        # Removing numeric values, stopwords and null ones
        line = [w for w in line if not ((w in self.stopwords) or (w.isnumeric()) or (w.isdigit()) or (w == ""))]
        # Stemming the tokens
        line = self.stemmer.stemWords(line)
        return line

    '''
        Tokenizer simple (first one, only used for tests and comparison)
    '''
    def tokenizeSimple(self, line):
        for c in self.denied_chars:
            line = line.replace(c, " ")
        line = ' '.join(word for word in line.split() if len(word)>self.min_token_size)
        line = line.lower().split(" ")
        return line
