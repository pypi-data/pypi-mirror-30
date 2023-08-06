.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/cp.svg
    :target: https://pypi.org/pypi/cp/
.. image:: https://img.shields.io/pypi/v/cp.svg
    :target: https://pypi.org/pypi/cp

|

.. image:: https://api.codacy.com/project/badge/Grade/08bbc04f25dd4bf59c29890ce87005a8
    :target: https://www.codacy.com/app/looking-for-a-job/cp.py
.. image:: https://codeclimate.com/github/looking-for-a-job/cp.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/cp.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/cp.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/cp.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=cp.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=cp.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=cp.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=cp.py

Install
```````


.. code:: bash

    `[sudo] pip install cp`

Usage
`````


.. code:: python

    >>> from cp import cp
    
    >>> cp(src,dst)


Examples
````````


.. code:: python

    >>> cp(src,dst)
    >>> cp(src,dst) # skip, exists
    >>> cp(src,dst,force=True) # force cp
