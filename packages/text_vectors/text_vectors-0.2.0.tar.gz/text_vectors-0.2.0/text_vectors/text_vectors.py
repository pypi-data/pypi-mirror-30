
from sklearn.base import TransformerMixin, BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
import os
from collections import defaultdict

WEIGHTS_PATH_50D = "https://github.com/chappers/text-vectors/releases/download/v0.1.0/glove.6B.50d.txt"
WEIGHTS_PATH_100D = "https://github.com/chappers/text-vectors/releases/download/v0.1.0/glove.6B.100d.txt"
WEIGHTS_PATH_200D = "https://github.com/chappers/text-vectors/releases/download/v0.1.0/glove.6B.200d.txt"
WEIGHTS_PATH_300D = "https://github.com/chappers/text-vectors/releases/download/v0.1.0/glove.6B.300d.txt"
WEIGHTS_PATH = 'http://nlp.stanford.edu/data/glove.6B.zip'

def get_file(fname,
                         origin,
                         untar=False,
                         md5_hash=None,
                         file_hash=None,
                         cache_subdir='datasets',
                         hash_algorithm='auto',
                         extract=False,
                         archive_format='auto',
                         cache_dir=None):
    """Downloads a file from a URL if it not already in the cache.
    By default the file at the url `origin` is downloaded to the
    cache_dir `~/.keras`, placed in the cache_subdir `datasets`,
    and given the filename `fname`. The final location of a file
    `example.txt` would therefore be `~/.keras/datasets/example.txt`.
    Files in tar, tar.gz, tar.bz, and zip formats can also be extracted.
    Passing a hash will verify the file after download. The command line
    programs `shasum` and `sha256sum` can compute the hash.
    Arguments:
            fname: Name of the file. If an absolute path `/path/to/file.txt` is
                    specified the file will be saved at that location.
            origin: Original URL of the file.
            untar: Deprecated in favor of 'extract'.
                    boolean, whether the file should be decompressed
            md5_hash: Deprecated in favor of 'file_hash'.
                    md5 hash of the file for verification
            file_hash: The expected hash string of the file after download.
                    The sha256 and md5 hash algorithms are both supported.
            cache_subdir: Subdirectory under the Keras cache dir where the file is
                    saved. If an absolute path `/path/to/folder` is
                    specified the file will be saved at that location.
            hash_algorithm: Select the hash algorithm to verify the file.
                    options are 'md5', 'sha256', and 'auto'.
                    The default 'auto' detects the hash algorithm in use.
            extract: True tries extracting the file as an Archive, like tar or zip.
            archive_format: Archive format to try for extracting the file.
                    Options are 'auto', 'tar', 'zip', and None.
                    'tar' includes tar, tar.gz, and tar.bz files.
                    The default 'auto' is ['tar', 'zip'].
                    None or an empty list will return no matches found.
            cache_dir: Location to store cached files, when None it
                    defaults to the [Keras
                        Directory](/faq/#where-is-the-keras-configuration-filed-stored).
    Returns:
            Path to the downloaded file
    """
    if cache_dir is None:
        cache_dir = os.path.join(os.path.expanduser('~'), '.keras')
    if md5_hash is not None and file_hash is None:
        file_hash = md5_hash
        hash_algorithm = 'md5'
    datadir_base = os.path.expanduser(cache_dir)
    if not os.access(datadir_base, os.W_OK):
        datadir_base = os.path.join('/tmp', '.keras')
    datadir = os.path.join(datadir_base, cache_subdir)
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    if untar:
        untar_fpath = os.path.join(datadir, fname)
        fpath = untar_fpath + '.tar.gz'
    else:
        fpath = os.path.join(datadir, fname)

    download = False
    if os.path.exists(fpath):
        # File found; verify integrity if a hash was provided.
        if file_hash is not None:
            if not validate_file(fpath, file_hash, algorithm=hash_algorithm):
                print('A local file was found, but it seems to be '
                            'incomplete or outdated because the ' + hash_algorithm +
                            ' file hash does not match the original value of ' + file_hash +
                            ' so we will re-download the data.')
                download = True
    else:
        download = True

    if download:
        print('Downloading data from', origin)

        class ProgressTracker(object):
            # Maintain progbar for the lifetime of download.
            # This design was chosen for Python 2.7 compatibility.
            progbar = None

        def dl_progress(count, block_size, total_size):
            if ProgressTracker.progbar is None:
                if total_size is -1:
                    total_size = None
                ProgressTracker.progbar = Progbar(total_size)
            else:
                ProgressTracker.progbar.update(count * block_size)

        error_msg = 'URL fetch failure on {}: {} -- {}'
        try:
            try:
                urlretrieve(origin, fpath, dl_progress)
            except URLError as e:
                raise Exception(error_msg.format(origin, e.errno, e.reason))
            except HTTPError as e:
                raise Exception(error_msg.format(origin, e.code, e.msg))
        except (Exception, KeyboardInterrupt) as e:
            if os.path.exists(fpath):
                os.remove(fpath)
            raise
        ProgressTracker.progbar = None

    if untar:
        if not os.path.exists(untar_fpath):
            _extract_archive(fpath, datadir, archive_format='tar')
        return untar_fpath

    if extract:
        _extract_archive(fpath, datadir, archive_format)

    return fpath




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
    
    def __init__(self, w2v=None, dimension='50d', glove_download=WEIGHTS_PATH, tfidf=False):
        self.glove_download = glove_download
        self.dimension = dimension
        self.w2v = w2v
        self.tfidf = tfidf
    
    def download_weights(self):
        try:
            cache_dir = os.path.join(os.path.expanduser('~'), '.keras')
            fpath = os.path.join(cache_dir, 'models', 'glove.6B.zip')
            if not os.path.isfile(fpath):
                from keras.utils import get_file as keras_get_file
                keras_path = keras_get_file('glove.6B.zip', WEIGHTS_PATH, extract=True, cache_subdir='models')
        except:
            pass
        if str(self.dimension).startswith('50'):
            weights_path = get_file('glove.6B.50d.txt', WEIGHTS_PATH_50D, cache_subdir='models')
        elif str(self.dimension).startswith('100'):
            weights_path = get_file('glove.6B.100d.txt', WEIGHTS_PATH_100D, cache_subdir='models')
        elif str(self.dimension).startswith('200'):
            weights_path = get_file('glove.6B.200d.txt', WEIGHTS_PATH_200D, cache_subdir='models')
        elif str(self.dimension).startswith('300'):
            # this won't work unless downloaded via keras_get_file
            weights_path = get_file('glove.6B.300d.txt', WEIGHTS_PATH_300D, cache_subdir='models')
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
        
        if self.tfidf:
            tfidf = TfidfVectorizer(analyzer=lambda x: x)
            tfidf.fit(X)
            max_idf = max(tfidf.idf_)
            self.word2weight = defaultdict(
                lambda: max_idf,
                [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
        
        return self
    
    def transform(self, X):
        if self.tfidf:
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


