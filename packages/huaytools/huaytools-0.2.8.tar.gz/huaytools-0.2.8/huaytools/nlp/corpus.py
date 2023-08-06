"""
语料处理相关常用函数
"""
import doctest
import pathlib

from huaytools.nlp.stopwords import NLTK


def remove_stopwords(tokens, stopwords=None, encoding='utf8'):
    """remove stopwords

    Args:
        tokens(list of str): a list of tokens/words
        stopwords(list of str or str): a list of words or a filepath

    Examples:
        >>> remove_stopwords(['huay', 'the'], ['the'])
        ['huay']

        >>> remove_stopwords(['huay', 'the'], 'stopwords_en')
        ['huay']

    """
    if stopwords is None:
        stopwords = NLTK.stopwords_en
    elif isinstance(stopwords, str) and pathlib.Path(stopwords).is_file():
        with open(stopwords, encoding=encoding) as f:
            stopwords = set(word.strip() for word in f if not word.isspace())
    else:
        stopwords = set(stopwords)

    return [w for w in tokens if w not in stopwords]


def clear_str_en(text):
    """clear the en text

    """


if __name__ == '__main__':
    """"""
    doctest.testmod()

    # with open('stopwords_en', encoding='utf8') as f:
    #     stopwords = set(word.strip() for word in f if not word.isspace())
    #     print(stopwords)