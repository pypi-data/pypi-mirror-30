.. image:: https://img.shields.io/pypi/pyversions/cached.svg
    :target: https://pypi.org/pypi/cached/

|

.. image:: https://api.codacy.com/project/badge/Grade/cfa863da31c84f0bab4065f12dc3f061
    :target: https://www.codacy.com/app/looking-for-a-job/cached.py
.. image:: https://www.codefactor.io/repository/github/looking-for-a-job/cached.py/badge
    :target: https://www.codefactor.io/repository/github/looking-for-a-job/cached.py
.. image:: https://codeclimate.com/github/looking-for-a-job/cached.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/cached.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/cached.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/cached.py/
.. image:: https://bettercodehub.com/edge/badge/looking-for-a-job/cached.py?branch=master
    :target: https://bettercodehub.com/results/looking-for-a-job/cached.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=cached.py&metric=code_smells
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



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/cached.py.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/cached.py.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/cached.py

.. image:: https://img.shields.io/github/issues/looking-for-a-job/cached.py.svg
    :target: https://github.com/looking-for-a-job/cached.py/issues
