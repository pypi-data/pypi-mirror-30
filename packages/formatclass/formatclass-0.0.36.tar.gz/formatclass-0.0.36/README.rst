.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/formatclass.svg
    :target: https://pypi.org/pypi/formatclass/
.. image:: https://img.shields.io/pypi/v/formatclass.svg
    :target: https://pypi.org/pypi/formatclass

|

.. image:: https://api.codacy.com/project/badge/Grade/03a5e45d1d03438cad6b4f74432eb743
    :target: https://www.codacy.com/app/looking-for-a-job/formatclass.py
.. image:: https://codeclimate.com/github/looking-for-a-job/formatclass.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/formatclass.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/formatclass.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/formatclass.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=formatclass.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=formatclass.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=formatclass.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=formatclass.py

Install
```````


.. code:: bash

    `[sudo] pip install formatclass`

Usage
`````


.. code:: python

    >>> from formatclass import formatclass
    
    >>> formatclass(cls)


Examples
````````


.. code:: python

    >>> class Cls(object): pass
    >>> class Cls2(Cls): 
        def __init__(self,arg,arg2="default"): pass
    
    # default
    >>> formatclass(CLS2)
    'Cls2(__main__.Cls)(arg, arg2="default")'
    
    # args - False/True (default True)
    >>> formatclass(CLS2,args=False)
    'Cls2(__main__.Cls)'
    
    # fullname - False/True (default True)
    >>> formatclass(CLS2,fullname=False)
    'Cls2(Cls)(arg, arg2="default")'
