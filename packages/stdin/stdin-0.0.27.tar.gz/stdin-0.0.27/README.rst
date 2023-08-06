.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/stdin.svg
    :target: https://pypi.org/pypi/stdin/
.. image:: https://img.shields.io/pypi/v/stdin.svg
    :target: https://pypi.org/pypi/stdin

|

.. image:: https://api.codacy.com/project/badge/Grade/8dd159f87e8b4662a3905e59ae14acce
    :target: https://www.codacy.com/app/looking-for-a-job/stdin.py
.. image:: https://codeclimate.com/github/looking-for-a-job/stdin.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/stdin.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/stdin.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/stdin.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=stdin.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=stdin.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=stdin.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=stdin.py

Install
```````


.. code:: bash

    `[sudo] pip install stdin`

Usage
`````


.. code:: python

    >>> from stdin import STDIN


Examples
````````


.. code:: bash

    $ echo "stdin text" | python -c "import stdin;print(stdin.STDIN)"
    stdin text
    
    $ python -c "import stdin;print(stdin.STDIN)"
    None
