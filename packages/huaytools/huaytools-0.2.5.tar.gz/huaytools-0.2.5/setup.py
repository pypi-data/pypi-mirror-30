"""
* Project Name: huaytools
* Author: huay
* Mail: imhuay@163.com
* Created Time:  2018-1-26 11:33:13
"""
from setuptools import setup, find_packages

install_requires = [
    'six',
    'bs4',
    'bunch',

    # Use Anaconda to install avoid install failed
    # 'tensorflow',
    # 'gensim',
    # 'numpy',
]

setup(
    name="huaytools",
    version="0.2.5",
    keywords=("huay", "huaytools"),
    description="huay's tools",
    long_description="huay's tools",
    license="MIT Licence",
    url="https://github.com/imhuay/huaytools",
    author="huay",
    author_email="imhuay@163.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=install_requires
)
