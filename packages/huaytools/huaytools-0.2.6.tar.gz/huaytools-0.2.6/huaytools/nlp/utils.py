"""
Common tool functions
"""
import re
import doctest

TOKENIZER_RE = re.compile(r"[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+",
                          re.UNICODE)


def tokenizer(iterator, tokenizer_re=TOKENIZER_RE):
    """Tokenizer generator.

    Examples:
        >>> list(tokenizer(["'sss'", 'dsa2ds', '3$ dasd']))

    Args:
        iterator: Input iterator with strings.
        tokenizer_re:

    Yields:
        array of tokens per each value in the input.
    """
    for value in iterator:
        yield tokenizer_re.findall(value)


if __name__ == '__main__':
    doctest.testmod()
