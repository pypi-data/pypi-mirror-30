.. image:: https://img.shields.io/badge/language-Python-blue.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/growlnotify.svg
    :target: https://pypi.org/pypi/growlnotify/
.. image:: https://img.shields.io/pypi/v/growlnotify.svg
    :target: https://pypi.org/pypi/growlnotify

|

.. image:: https://api.codacy.com/project/badge/Grade/b3ea7786516b42dfbb667cbe4fbf6d52
    :target: https://www.codacy.com/app/looking-for-a-job/growlnotify.py
.. image:: https://codeclimate.com/github/looking-for-a-job/growlnotify.py/badges/gpa.svg
    :target: https://codeclimate.com/github/looking-for-a-job/growlnotify.py
.. image:: https://img.shields.io/scrutinizer/g/looking-for-a-job/growlnotify.py.svg
    :target: https://scrutinizer-ci.com/g/looking-for-a-job/growlnotify.py/
.. image:: https://sonarcloud.io/api/project_badges/measure?project=growlnotify.py&metric=code_smells
    :target: https://sonarcloud.io/dashboard?id=growlnotify.py
.. image:: https://sonarcloud.io/api/project_badges/measure?project=growlnotify.py&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=growlnotify.py

Install
```````


.. code:: bash

    `[sudo] pip install growlnotify`

Usage
`````


.. code:: python

    >>> from growlnotify import growlnotify
    
    >>> growlnotify(title,message,)


Examples
````````


.. code:: python

    >>> growlnotify("title")
    
    >>> growlnotify(u"unicode") # unicode
    
    >>> growlnotify("title",message="message") # message
    
    >>> growlnotify("title",sticky=True) # sticky
    
    import os
    >>> growlnotify("title",message="message",app="Finder",url="file://%s" % os.environ["HOME"])
