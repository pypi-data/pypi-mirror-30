
import warnings

from text_vectors.text_vectors import TextVec

try:
    from text_vectors.version import version as __version__
except:
    warnings.warn("Could not import version, has `text_vectors` been installed?")
