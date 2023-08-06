.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/dict.svg
    :target: https://pypi.org/pypi/dict/
.. image:: https://img.shields.io/pypi/v/dict.svg
    :target: https://pypi.org/pypi/dict

|

.. image:: https://api.codacy.com/project/badge/Grade/60d350ee07c74bd181d23b2f3c9e7430
    :target: https://www.codacy.com/app/looking-for-a-job/dict.py
.. image:: https://codeclimate.com/github/looking-for-a-job/dict.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/dict.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/dict.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/dict.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=dict.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=dict.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=dict.py&metric=reliability_rating
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
