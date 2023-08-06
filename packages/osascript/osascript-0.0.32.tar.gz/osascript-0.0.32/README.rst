.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/osascript.svg
    :target: https://pypi.org/pypi/osascript/
.. image:: https://img.shields.io/pypi/v/osascript.svg
    :target: https://pypi.org/pypi/osascript

|

.. image:: https://api.codacy.com/project/badge/Grade/0602d537ebdd4a059139afbf07b43fc5
    :target: https://www.codacy.com/app/looking-for-a-job/osascript.py
.. image:: https://codeclimate.com/github/looking-for-a-job/osascript.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/osascript.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/osascript.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/osascript.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=osascript.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=osascript.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=osascript.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=osascript.py

Install
```````


.. code:: bash

    `[sudo] pip install osascript`

Usage
`````


.. code:: python

    >>> from osascript import osascript
    
    >>> returncode,stdout,stderr = osascript(code)


Examples
````````


.. code:: python

    >>> returncode,stdout,stderr = osascript('display dialog "42"')
