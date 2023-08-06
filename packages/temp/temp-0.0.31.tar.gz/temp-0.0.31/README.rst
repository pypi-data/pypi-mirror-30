.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/temp.svg
    :target: https://pypi.org/pypi/temp/
.. image:: https://img.shields.io/pypi/v/temp.svg
    :target: https://pypi.org/pypi/temp

|

.. image:: https://api.codacy.com/project/badge/Grade/58d851db667e4e21af9d7381b365a1c3
    :target: https://www.codacy.com/app/looking-for-a-job/temp.py
.. image:: https://codeclimate.com/github/looking-for-a-job/temp.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/temp.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/temp.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/temp.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=temp.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=temp.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=temp.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=temp.py

Install
```````


.. code:: bash

    `[sudo] pip install temp`

Usage
`````


.. code:: python

    >>> from temp import tempdir, tempfile, TMPDIR
    
    >>> tempdir() # dir
    >>> tempfile() # file


Examples
````````


.. code:: python

    >>> tempdir() # dir
    '/var/folders/rv/gy6_gnfs1d7_pd1518p27tsr0000gn/T/tmpqlLDxb'
    
    >>> tempfile() # file
    '/var/folders/rv/gy6_gnfs1d7_pd1518p27tsr0000gn/T/tmpsctFHJ'
    
    >>> TMPDIR
    '/var/folders/rv/gy6_gnfs1d7_pd1518p27tsr0000gn/T'
