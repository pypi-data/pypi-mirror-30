.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/public.svg
    :target: https://pypi.org/pypi/public/
.. image:: https://img.shields.io/pypi/v/public.svg
    :target: https://pypi.org/pypi/public

|

.. image:: https://api.codacy.com/project/badge/Grade/535736e5a8d148369e9bc237238b3831
    :target: https://www.codacy.com/app/looking-for-a-job/public.py
.. image:: https://codeclimate.com/github/looking-for-a-job/public.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/public.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/public.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/public.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=public.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=public.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=public.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=public.py

Install
```````


.. code:: bash

    `[sudo] pip install public`

Usage
`````


.. code:: python

    >>> from public import public
    
    >>> @public # decorator
    
    >>> public(*objects) # function


Examples
````````


.. code:: python

    >>> @public
    	def func(): pass
    
    >>> @public
    	class CLS: pass
    
    >>> print(__all__)
    ['CLS',func']
    
    # public(*objects) function
    >>> public("name")
    >>> public("name1","name2")
    
    >>> print(__all__)
    ['name','name1','name2']
