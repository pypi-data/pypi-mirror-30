# huaytools 

主要用于记录一些有用但又不太常用的小脚本、小函数，避免每次 Google，想起来的时候总是差一口气

## 主要模块

- utils: 使用 Python API 集成的一些固定的使用方式，比如文件处理，时间处理等
- nlp: 自然语言处理相关，如停用词处理，数据清洗等
- template: 用于保存一些模板代码，方便查看，没有什么功能
- crawler: 爬虫相关，不过在我开始维护这个 PyPI 库的时候，已经很少使用爬虫了，所以基本没添加什么函数

## 使用 PyPI 发布与维护自己的模块

下面简述如何使用 PyPI 发布与维护自己的模块

> CSDN/[python如何发布自已pip项目](http://blog.csdn.net/fengmm521/article/details/79144407)
> 该博客介绍了主要的流程，但是部分操作依据过时了

1. [注册自己的 PyPI 账户](https://pypi.python.org/pypi?%3Aaction=register_form)
2. 创建项目，并发布到 github （并不是必要的步骤，但是建议这么做）
3. 编写 setup.py 文件 (参考)
    ```python
    """
    * Project Name: Tensorflow Template
    * Author: huay
    * Mail: imhuay@163.com
    * Created Time:  2018-3-20 17:49:53
    """
    from setuptools import setup, find_packages
    
    install_requires = [
        'bunch',
        # 'tensorflow',  # install it beforehand
    ]
    
    setup(
        name="tensorflow_template",
        version="0.2",
        keywords=("huay", "tensorflow", "template", "tensorflow template"),
        description="A tensorflow template for quick starting a deep learning project.",
        long_description="A deep learning template with tensorflow...",
        license="MIT Licence",
        url="https://github.com/imhuay/tensorflow_template",
        author="huay",
        author_email="imhuay@163.com",
        packages=find_packages(),
        include_package_data=True,
        platforms="any",
        install_requires=install_requires
    )
    ```
    校验 setup.py
    ```
    > python setup.py check
    ```
4. 创建 `$HOME/.pypirc` 文件保存 PyPI 账户信息
    ```
    [distutils]
    index-servers = pypi
    
    [pypi]
    repository: https://upload.pypi.org/legacy/
    username: imhuay
    password = ***
    ```
    > 这里使用 : 和 = 都可以
    
5. 打包并上传
    ```
    > python setup.py sdist
    > twine upload dist/huaytools-VERSION.tar.gz
    ```
    如果没有 twine，需要先安装
    ```
    pip install twine
    ```
   PS: python setup.py upload 已经弃用
6. 上传成功，就可以在 https://pypi.python.org/pypi 查看刚刚上传的项目了
7. 接下来就可以 pip 自己刚刚发布的项目了（如果你没有改过 pip 源的话）