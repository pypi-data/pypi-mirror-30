
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer

from keras.utils import get_file
import numpy as np
from collections import defaultdict

WEIGHTS_PATH_50D = "https://github.com/chappers/text-vectors/releases/download/v0.1.0/glove.6B.50d.txt"

class TextVec(TransformerMixin, BaseEstimator):
    """
    This is a pipeline-able object which uses GLOVE. It does nothing else
    """
    
    @staticmethod
    def convert_str(x):
        try:
            return x.decode('ascii')
        except:
            return x
    
    def __init__(self, w2v=None, dimension='50d', glove_download=WEIGHTS_PATH_50D, method='tfidf'):
        self.glove_download = glove_download
        self.dimension = dimension
        self.w2v = w2v
        self.method = method
    
    def download_weights(self):
        if self.dimension == '50d':
            weights_path = get_file('glove.6B.50d.txt', WEIGHTS_PATH_50D, cache_subdir='models')
        else:
            weights_path = get_file('glove.6B.50d.txt', WEIGHTS_PATH_50D, cache_subdir='models')
        with open(weights_path, "rb") as lines:
            w2v = {self.convert_str(line.split()[0]): np.array([float(x) for x in line.split()[1:]])
                   for line in lines}
        
        self.w2v = w2v
        self.dim = len(self.w2v.keys())
    
    def fit(self, X, y=None):
        if self.w2v is None:
            self.download_weights()
        
        if self.method == 'tfidf':
            tfidf = TfidfVectorizer(analyzer=lambda x: x)
            tfidf.fit(X)
            max_idf = max(tfidf.idf_)
            self.word2weight = defaultdict(
                lambda: max_idf,
                [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
        
        return self
    
    def transform(self, X):
        if self.method == 'tfidf':
            return np.array([
                np.mean([self.w2v[w] * self.word2weight[w]
                         for w in words if w in self.w2v] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])
        else:
            return np.array([
                np.mean([self.w2v[w] for w in words if w in self.w2v]
                        or [np.zeros(self.dim)], axis=0)
                for words in X
            ])


