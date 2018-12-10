import pickle
class Code2Vec:
    def __init__(self):
        self.vocab_methname = self.load_pickle("./data/github/vocab.methname.pkl")
        self.vocab_apiseq=self.load_pickle("./data/github/vocab.apiseq.pkl")
        self.vocab_tokens=self.load_pickle("./data/github/vocab.tokens.pkl")
    def load_pickle(self, filename):
        f = open(filename, 'rb')
        data = pickle.load(f)
        f.close()
        return data   
    def convert(self, vocab, words):
        """convert words into indices"""
        if type(words) == str:
            words = words.strip().lower().split(' ')
        return [vocab.get(w, 0) for w in words]
    def convert_methname(self, words):
        return self.convert(self.vocab_methname, words)
    def convert_apiseq(self, words):
        return self.convert(self.vocab_apiseq, words)
    def convert_tokens(self, words):
        return self.convert(self.vocab_tokens, words)