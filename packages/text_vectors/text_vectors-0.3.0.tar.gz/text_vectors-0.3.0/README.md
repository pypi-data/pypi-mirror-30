# text-vectors

Text vector leverages GloVe using the provided by the [Stanford Group](https://nlp.stanford.edu/projects/glove/), and other data sources within [`gensim-data`](https://github.com/RaRe-Technologies/gensim-data). 

The goal is to provide pre-trained models or sensible defaults for a variety of models that can interact with scikit-learn for the purposes of feature extraction. This is an _opinionated_ approach to make it easier to get started with Machine Learning with text mining in a more automated approach.

## Installation

```
pip install text_vectors
```

## Example Usage

```py
# by default uses GloVe 50d
from text_vectors import TextVec
tv = TextVec()

tv.fit_transform(["hello world".split(" ")])

# loading fasttext model with 300d
import gensim.downloader as api
model = api.load("fasttext-wiki-news-subwords-300")
model = TextVec(model)

model.transform([["hello world".split(" ")]])
```

