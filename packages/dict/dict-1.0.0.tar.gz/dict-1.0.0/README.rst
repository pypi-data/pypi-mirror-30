.. image:: https://img.shields.io/pypi/pyversions/dict.svg
    :target: https://pypi.org/pypi/dict/

|

.. image:: https://api.codacy.com/project/badge/Grade/60d350ee07c74bd181d23b2f3c9e7430
    :target: https://www.codacy.com/app/looking-for-a-job/dict.py
.. image:: https://www.codefactor.io/repository/github/looking-for-a-job/dict.py/badge
    :target: https://www.codefactor.io/repository/github/looking-for-a-job/dict.py
.. image:: https://codeclimate.com/github/looking-for-a-job/dict.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/dict.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/dict.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/dict.py/
.. image:: https://bettercodehub.com/edge/badge/looking-for-a-job/dict.py?branch=master
    :target: https://bettercodehub.com/results/looking-for-a-job/dict.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=dict.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=dict.py

Install
```````


.. code:: bash

    `[sudo] pip install dict`

Features
````````


*	**attribute-style access**
* 	**None** instead of **KeyError**
* 	safe **remove**
* 	jQuery like **methods chaining**

Usage
`````


.. code:: python

    >>> from dict import dict


Examples
````````


.. code:: python

    >>> dict(k="v")["k"]
    "v"
    
    >>>  dict(k="v").k
    "v"
    
    >>> dict(k="v")["not_existing"]
    None
    
    >>> dict(k="v").not_existing
    None
    
    >>> dict(k="v").get("K",i=True) # case insensitive



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/dict.py.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/dict.py.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/dict.py

.. image:: https://img.shields.io/github/issues/looking-for-a-job/dict.py.svg
    :target: https://github.com/looking-for-a-job/dict.py/issues
