"""工具函数（如果不知道应该归到哪个模块文件，就放在这里）
"""
import os
import sys
import platform
from typing import Iterable

import logging


if sys.version_info[0] >= 3:
    unicode = str


def yield_cycling(iterator):
    """
    无限循环迭代器

    itertools 提供了类似的方法
        from itertools import cycle

    Args:
        iterator (Iterable): 可迭代对象

    Examples:

        >>> it = yield_cycling([1, 2, 3])
        >>> for _ in range(4):
        ...     print(next(it))
        1
        2
        3
        1

    """
    while True:
        yield from iter(iterator)


def system_is(system_type):
    """
    判断系统类型

    Args:
        system_type(str): 系统类型，可选 "linux", "windows", ..

    Returns:
        bool

    Examples:
        >>> if system_is("windows"):
        ...     print("Windows")
        Windows

    """
    if system_type.lower().startswith('win'):
        system_type = 'Windows'
    else:
        system_type = 'Linux'
    return system_type == platform.system()


def system_is_windows():
    """
    If the system is windows, return True

    Examples:
        >>> if system_is_windows():
        ...     print("Windows")
        Windows
    """
    return system_is("Windows")


def get_logger(name=None, fname=None, mode='a', level=logging.INFO, stream=None,
               fmt="[%(name)s] : %(asctime)s : %(levelname)s : %(message)s"):
    """
    Default log to console. If `fname` is not None, if will log to the file at same time.

    Returns:


    Examples:
        >>> logger = get_logger(stream=sys.stdout, fmt="[%(name)s] : %(levelname)s : %(message)s")
        >>> logger.info("test")
        [tools.py] : INFO : test


    """
    # 虽然使用 root logger 可能会产生重复输出的问题，但为了能够同时输出不同的 handler，还是默认使用 root
    # if name is None:
    #     # name = os.path.splitext(os.path.basename(__file__))[0]
    #     name = os.path.basename(__file__)

    logger = logging.Logger(name)
    logger.setLevel(level)

    fmt = logging.Formatter(fmt)

    ch = logging.StreamHandler(stream)
    ch.setFormatter(fmt)

    logger.addHandler(ch)

    if fname is not None:
        fh = logging.FileHandler(fname, mode)
        fh.setFormatter(fmt)

        logger.addHandler(fh)

    return logger


def to_unicode(txt, encoding='utf8', errors='strict'):
    """Convert text to unicode.

    Args:
        txt:
        encoding:
        errors:

    Returns:
        str

    """

    if isinstance(txt, unicode):
        return txt
    return unicode(txt, encoding, errors=errors)


def get_var_name(**kwargs):
    """
    TODO(huay): It's useless.

    Get the literal name of var.
        s = 123
        it will return 's' rather than 123

    Examples:
        >>> s = 123
        >>> print(get_var_name(s=s))
        s

    Args:
        var:

    Returns:
        str

    """
    return list(kwargs.keys())[0]


def set_logging_basic_config(**kwargs):
    """
    Args can be specified:
        filename: Specifies that a FileHandler be created, using the specified
            filename, rather than a StreamHandler.
        filemode: Specifies the mode to open the file, if filename is specified
            (if filemode is unspecified, it defaults to 'a').
        format: Use the specified format string for the handler.
        datefmt: Use the specified date/time format.
        style: If a format string is specified, use this to specify the
            type of format string (possible values '%', '{', '$', for
            %-formatting, :meth:`str.format` and :class:`string.Template`
            - defaults to '%').
        level: Set the root logger level to the specified level.
        stream: Use the specified stream to initialize the StreamHandler. Note
            that this argument is incompatible with 'filename' - if both
            are present, 'stream' is ignored.
        handlers: If specified, this should be an iterable of already created
            handlers, which will be added to the root handler. Any handler
            in the list which does not have a formatter assigned will be
            assigned the formatter created in this function.

    Returns:
        None
    """
    if 'format' not in kwargs:
        kwargs['format'] = '[%(name)s] : %(asctime)s : %(levelname)s : %(message)s'
    if 'level' not in kwargs:
        kwargs['level'] = logging.INFO

    logging.basicConfig(**kwargs)
