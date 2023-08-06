============
LanguageFlow
============

.. image:: https://img.shields.io/pypi/v/languageflow.svg
        :target: https://pypi.python.org/pypi/underthesea

.. image:: https://img.shields.io/pypi/pyversions/languageflow.svg
        :target: https://pypi.python.org/pypi/underthesea

.. image:: https://img.shields.io/pypi/l/languageflow.svg
        :target: https://pypi.python.org/pypi/underthesea

.. image:: https://img.shields.io/travis/magizbox/underthesea.svg
        :target: https://travis-ci.org/magizbox/underthesea

.. image:: https://readthedocs.org/projects/languageflow/badge/?version=latest
        :target: http://languageflow.readthedocs.io/en/latest/
        :alt: Documentation Status

Data loaders and abstractions for text and NLP

Requirements
------------

Dependencies:

* future
* tox
* joblib
* pandas
* numpy
* scipy
* python-crfsuite
* scikit-learn==0.19.0
* fasttext==0.8.3
* xgboost

Install dependencies

.. code-block:: bash

    $ pip install joblib future numpy scipy pandas
    $ pip install scikit-learn==0.19.0
    $ pip install python-crfsuite==0.9.5
    $ pip install Cython
    $ pip install -U fasttext --no-cache-dir --no-deps --force-reinstall
    $ pip install xgboost


Installation
------------


Stable version

.. code-block:: bash

    $ pip install https://github.com/undertheseanlp/languageflow/archive/master.zip

Develop version

.. code-block:: bash

    $ pip install https://github.com/undertheseanlp/languageflow/archive/develop.zip
