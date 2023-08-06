.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/self.svg
    :target: https://pypi.org/pypi/self/
.. image:: https://img.shields.io/pypi/v/self.svg
    :target: https://pypi.org/pypi/self

|

.. image:: https://api.codacy.com/project/badge/Grade/34c672515f7b472fb120e9608979f47d
    :target: https://www.codacy.com/app/looking-for-a-job/self.py
.. image:: https://codeclimate.com/github/looking-for-a-job/self.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/self.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/self.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/self.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=self.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=self.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=self.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=self.py

Install
```````


.. code:: bash

    `[sudo] pip install self`

Usage
`````


.. code:: python

    >>> from self import self
    
    >>> @self
    	def method(self):


Examples
````````


.. code:: python

    >>> class CLS:
    	@self
    	def method(self):
    		print("test")
    
    	@self
    	def method2(self):
    		print("test")
    
    >>> CLS().method().method2() # jQuery like chain
