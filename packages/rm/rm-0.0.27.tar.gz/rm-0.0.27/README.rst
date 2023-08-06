.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/rm.svg
    :target: https://pypi.org/pypi/rm/
.. image:: https://img.shields.io/pypi/v/rm.svg
    :target: https://pypi.org/pypi/rm

|

.. image:: https://api.codacy.com/project/badge/Grade/59291adefe0b4daeb39f5a3f5666f273
    :target: https://www.codacy.com/app/looking-for-a-job/rm.py
.. image:: https://codeclimate.com/github/looking-for-a-job/rm.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/rm.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/rm.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/rm.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=rm.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=rm.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=rm.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=rm.py

Install
```````


.. code:: bash

    `[sudo] pip install rm`

Features
````````

- **dirs** and **files** supported
- **~**, **..**, **.** expand
- **no exception** if path not exists

Usage
`````


.. code:: python

    >>> from rm import rm
    
    >>> rm(path)


Examples
````````


.. code:: python

    >>> rm("path/to/file")
    >>> rm("path/to/dir")
    >>> rm("not-existing") # no exception
