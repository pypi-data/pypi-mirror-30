"""
Handle the different kinds of word embedding
    * word2vec
    * GloVe
    * FastText
"""
import doctest
import logging
from numpy import float32
from gensim.models import KeyedVectors

logger = logging.getLogger(__name__)


class BasicFormatWV:
    """
    The basic word vector format is the original C word2vec-tool format (text and binary).
    The first line is `vocab_size vector_size`, than are `token wordvec`. Which like
        ```
        2519370 300
        the -0.065334 -0.093031 -0.017571 ...
        of 0.048804 -0.28528 0.018557 ...
        ```
    """

    def __init__(self, fname, load_at_once=False):
        """

        """
        self.fname = fname
        self.word2vec = None
        self.word2id = dict()

        if load_at_once:
            self.load(fname)

    def load(self, fname=None, fvocab=None, binary=False, encoding='utf8', unicode_errors='strict', limit=None,
             datatype=float32):
        if fname is None:
            fname = self.fname

        self.word2vec = KeyedVectors.load_word2vec_format(fname,
                                                          fvocab=fvocab, binary=binary,
                                                          encoding=encoding, unicode_errors=unicode_errors,
                                                          limit=limit, datatype=datatype)
        return self

    def get_word2id_dict(self):
        """Build the word2id dict from the pre-train wordvec

        Examples:
            >>> wv_path = "D:/OneDrive/workspace/data/nlp/word2vec/fastText/wiki.en.vec"
            >>> basic_format_wv = BasicFormatWV(wv_path)
            >>> _ = basic_format_wv.load(limit=100)
            >>> word2id = basic_format_wv.get_word2id_dict()

        """
        if self.word2vec is None:
            logger.error("Load the wordvec first.")

        for k, v in self.word2vec.vocab.items():
            self.word2id[k] = v.index

        return self.word2id


class FastText:
    """
    The process to use FastText Word embedding
    """

    def load(self):
        """"""


if __name__ == '__main__':
    """"""
    doctest.testmod()
