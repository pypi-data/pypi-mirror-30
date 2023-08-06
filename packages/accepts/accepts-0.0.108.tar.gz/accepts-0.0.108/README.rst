.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/accepts.svg
    :target: https://pypi.org/pypi/accepts/
.. image:: https://img.shields.io/pypi/v/accepts.svg
    :target: https://pypi.org/pypi/accepts

|

.. image:: https://api.codacy.com/project/badge/Grade/81a64e612bec41c4afe6fc3901daa88a
    :target: https://www.codacy.com/app/looking-for-a-job/accepts.py
.. image:: https://codeclimate.com/github/looking-for-a-job/accepts.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/accepts.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/accepts.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/accepts.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=accepts.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=accepts.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=accepts.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=accepts.py

Install
```````


.. code:: bash

    `[sudo] pip install accepts`

Features
````````

*	support **multiple types** argument
*	support **None** argument
*	human readable detailed exception message

Usage
`````


.. code:: python

    >>> from accepts import accepts
    
    >>> @accepts(arg1type,arg2type,...)


Examples
````````


.. code:: python

    >>> @accepts(int)
    def inc(value):
    	return value+1
    
    >>> inc(1) # ok
    >>> inc(1.5) # exception
    TypeError: ....
    
    # multiple types
    >>> @accepts((int,float))
    
    # None
    >>> @accepts((int,float,type(None)))
