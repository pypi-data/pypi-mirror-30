.. image:: https://img.shields.io/pypi/pyversions/write.svg
    :target: https://pypi.org/pypi/write/

|

.. image:: https://api.codacy.com/project/badge/Grade/075eda6d69fa422f86a26f093ddcf26d
    :target: https://www.codacy.com/app/looking-for-a-job/write.py
.. image:: https://www.codefactor.io/repository/github/looking-for-a-job/write.py/badge
    :target: https://www.codefactor.io/repository/github/looking-for-a-job/write.py
.. image:: https://codeclimate.com/github/looking-for-a-job/write.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/write.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/write.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/write.py/
.. image:: https://bettercodehub.com/edge/badge/looking-for-a-job/write.py?branch=master
    :target: https://bettercodehub.com/results/looking-for-a-job/write.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=write.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=write.py

Install
```````


.. code:: bash

    `[sudo] pip install write`

Usage
`````


.. code:: python

    >>> from write import write
    
    >>> write(path,text)


Examples
````````


.. code:: python

    >>> write(path,'string')
    >>> open(path).read()
    'string'
    
    >>> write(path,None) # touch
    >>> open(path).read()
    ''
    
    >>> write(path,42) # write integer
    >>> open(path).read()
    '42'
    
    >>> write(path,dict()) # converted to str
    >>> open(path).read()
    '{}'



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/write.py.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/write.py.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/write.py

.. image:: https://img.shields.io/github/issues/looking-for-a-job/write.py.svg
    :target: https://github.com/looking-for-a-job/write.py/issues
