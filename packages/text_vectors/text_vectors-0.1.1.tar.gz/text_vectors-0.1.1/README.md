# text-vectors

Text vector leverages GloVe using the provided by the [Stanford Group](https://nlp.stanford.edu/projects/glove/)

## Installation

```
pip install text_vectors
```

## Example Usage

```py
from text_vectors import TextVec
tv = TextVec()

tv.fit_transform(["hello world".split(" ")])
```

