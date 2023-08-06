.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/rreplace.svg
    :target: https://pypi.org/pypi/rreplace/
.. image:: https://img.shields.io/pypi/v/rreplace.svg
    :target: https://pypi.org/pypi/rreplace

|

.. image:: https://api.codacy.com/project/badge/Grade/65006c19e58e4d4b91a9950f0f56d8ef
    :target: https://www.codacy.com/app/looking-for-a-job/rreplace.py
.. image:: https://codeclimate.com/github/looking-for-a-job/rreplace.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/rreplace.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/rreplace.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/rreplace.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=rreplace.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=rreplace.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=rreplace.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=rreplace.py

Install
```````


.. code:: bash

    `[sudo] pip install rreplace`

Usage
`````


.. code:: python

    >>> from rreplace import rreplace
    
    >>> rreplace(string,old,new,count=None)


Examples
````````


.. code:: python

    >>> rreplace('old_old','old','new',1))
    'old_new'
