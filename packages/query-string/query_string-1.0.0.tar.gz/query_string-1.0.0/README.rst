.. image:: https://img.shields.io/pypi/pyversions/query_string.svg
    :target: https://pypi.org/pypi/query_string/

|

.. image:: https://api.codacy.com/project/badge/Grade/da7cca99ede548f9aa1ac583d39f4afd
    :target: https://www.codacy.com/app/looking-for-a-job/query_string.py
.. image:: https://www.codefactor.io/repository/github/looking-for-a-job/query_string.py/badge
    :target: https://www.codefactor.io/repository/github/looking-for-a-job/query_string.py
.. image:: https://codeclimate.com/github/looking-for-a-job/query_string.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/query_string.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/query_string.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/query_string.py/
.. image:: https://bettercodehub.com/edge/badge/looking-for-a-job/query_string.py?branch=master
    :target: https://bettercodehub.com/results/looking-for-a-job/query_string.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=query_string.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=query_string.py

Install
```````


.. code:: bash

    `[sudo] pip install query_string`

Usage
`````


.. code:: python

    >>> from query_string import query_string
    
    >>> query_string(url)


Examples
````````


.. code:: python

    >>> query_string('https://site.org/index.php?k=v&k2=v2&k3=v3#anchor')
    {'k': 'v','k2': 'v2', 'k3': 'v3'}
    
    >>> query_string('k=v&k2=v2&k3=v3')
    {'k': 'v','k2': 'v2', 'k3': 'v3'}



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/query_string.py.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/query_string.py.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/query_string.py

.. image:: https://img.shields.io/github/issues/looking-for-a-job/query_string.py.svg
    :target: https://github.com/looking-for-a-job/query_string.py/issues
