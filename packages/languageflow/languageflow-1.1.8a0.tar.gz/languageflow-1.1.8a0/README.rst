============
LanguageFlow
============

.. image:: https://img.shields.io/pypi/v/languageflow.svg
        :target: https://pypi.python.org/pypi/languageflow

.. image:: https://img.shields.io/pypi/pyversions/languageflow.svg
        :target: https://pypi.python.org/pypi/languageflow

.. image:: https://img.shields.io/pypi/l/languageflow.svg
        :target: https://pypi.python.org/pypi/languageflow

.. image:: https://img.shields.io/travis/undertheseanlp/languageflow.svg
        :target: https://travis-ci.org/undertheseanlp/languageflow

.. image:: https://readthedocs.org/projects/languageflow/badge/?version=latest
        :target: http://languageflow.readthedocs.io/en/latest/
        :alt: Documentation Status

Data loaders and abstractions for text and NLP

Requirements
------------

Dependencies:

* future, tox, joblib
* numpy, scipy, pandas, scikit-learn==0.19.0
* python-crfsuite
* fasttext==0.8.3
* xgboost

Install dependencies

.. code-block:: bash

    $ pip install future, tox, joblib
    $ pip install numpy scipy pandas scikit-learn==0.19.0
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
