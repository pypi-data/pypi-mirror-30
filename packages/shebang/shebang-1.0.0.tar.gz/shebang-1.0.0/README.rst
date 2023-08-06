.. image:: https://img.shields.io/pypi/pyversions/shebang.svg
    :target: https://pypi.org/pypi/shebang/

|

.. image:: https://api.codacy.com/project/badge/Grade/d6ba7ecf67b24670b17d56b4d5d5ded4
    :target: https://www.codacy.com/app/looking-for-a-job/shebang.py
.. image:: https://www.codefactor.io/repository/github/looking-for-a-job/shebang.py/badge
    :target: https://www.codefactor.io/repository/github/looking-for-a-job/shebang.py
.. image:: https://codeclimate.com/github/looking-for-a-job/shebang.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/shebang.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/shebang.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/shebang.py/
.. image:: https://bettercodehub.com/edge/badge/looking-for-a-job/shebang.py?branch=master
    :target: https://bettercodehub.com/results/looking-for-a-job/shebang.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=shebang.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=shebang.py

Install
```````


.. code:: bash

    `[sudo] pip install shebang`

Usage
`````


.. code:: python

    >>> from shebang import shebang
    
    >>> shebang(path)


Examples
````````


.. code:: python

    >>> shebang("path/to/file.py")
    '/usr/bin/env python'
    
    >>> shebang("path/to/file.txt")
    None
    
    shebang("/bin/test")
    None



Feedback



.. image:: https://img.shields.io/github/issues/looking-for-a-job/shebang.py.svg
    :target: https://github.com/looking-for-a-job

.. image:: https://img.shields.io/github/stars/looking-for-a-job/shebang.py.svg?style=social&label=Stars
    :target: https://github.com/looking-for-a-job/shebang.py

.. image:: https://img.shields.io/github/issues/looking-for-a-job/shebang.py.svg
    :target: https://github.com/looking-for-a-job/shebang.py/issues
