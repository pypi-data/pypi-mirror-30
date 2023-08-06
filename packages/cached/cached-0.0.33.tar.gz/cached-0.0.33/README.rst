.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/cached.svg
    :target: https://pypi.org/pypi/cached/
.. image:: https://img.shields.io/pypi/v/cached.svg
    :target: https://pypi.org/pypi/cached

|

.. image:: https://api.codacy.com/project/badge/Grade/cfa863da31c84f0bab4065f12dc3f061
    :target: https://www.codacy.com/app/looking-for-a-job/cached.py
.. image:: https://codeclimate.com/github/looking-for-a-job/cached.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/cached.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/cached.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/cached.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=cached.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=cached.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=cached.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=cached.py

Install
```````


.. code:: bash

    `[sudo] pip install cached`

Usage
`````


.. code:: python

    >>> from cached import cached
    
    >>> cached(func)()


Examples
````````


.. code:: python

    >>> def func(*args,**kwags):
    	print('log')
    	return "result"
    
    >>> cached(func)()
    log
    'result'
    >>> cached(func)() # cached :)
    'result'
