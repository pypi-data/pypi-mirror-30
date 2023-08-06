
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer

import gensim.downloader as api

import numpy as np
import os
from collections import defaultdict

class TextVec(TransformerMixin, BaseEstimator):
    """
    This is a pipeline-able object which uses GLOVE. It does nothing else
    
    Supported Dimensions: 50, 100, 200, 300 
    glove_download: path to `glove.6B.zip`, this is supported only if keras is installed
    tfidf: are vectors to be trained via TFIDF in conjunction with GloVe?
    """
    
    @staticmethod
    def convert_str(x):
        try:
            return x.decode('ascii')
        except:
            return x
    
    def __init__(self, model=None, api_path="glove-wiki-gigaword-50", dim=None, tfidf=False):
        self.api_path = api_path
        self.model = model
        self.tfidf = tfidf
        self.dim = dim
    
    def download_weights(self):
        model = api.load(self.api_path)
        self.model = model
        self.dim = len(self.model.keys())
    
    def fit(self, X, y=None):
        if self.model is None:
            self.download_weights()
        elif 'keys' in dir(self.model):
            self.dim = len(self.model.keys())
        elif 'vector_size' in dir(self.model):
            self.dim = self.model.vector_size
        
        if self.tfidf:
            tfidf = TfidfVectorizer(analyzer=lambda x: x)
            tfidf.fit(X)
            max_idf = max(tfidf.idf_)
            self.word2weight = defaultdict(
                lambda: max_idf,
                [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
        
        return self
    
    def gensim_transform(self, words):
        return np.mean([self.model.get_vector(w) for w in words if w in self.model.vocab.keys()]
                        or [np.zeros(self.dim)], axis=0)
    
    def transform(self, X):
        if self.tfidf:
            return np.array([
                np.mean([self.model[w] * self.word2weight[w]
                         for w in words if w in self.model] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])
        if 'gensim' in str(type(self.model)):
            return np.array([self.gensim_transform(words) for words in X])
        return np.array([
                np.mean([self.model[w] for w in words if w in self.model]
                        or [np.zeros(self.dim)], axis=0)
                for words in X
            ])


