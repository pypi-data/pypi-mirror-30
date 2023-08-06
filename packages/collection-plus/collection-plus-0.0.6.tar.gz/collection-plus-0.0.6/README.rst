Description
------------
List of collections similar to JAVA style collection for Python

Installation
============

::

    $ pip install collection-plus


Usage
=====

.. code-block:: python

    from collection import *

    l = List()
    l.add(1)
    l.is_empty()

    vec = Vector()
    vec.add(1)

    stack = Stack()
    stack.push(1)
    stack.pop()
    item = stack.peek()

    queue = Queue()
    queue.offer(1)
    item = queue.peek()
    queue.poll()

Build Project
=============
source distribution: python setup.py sdist
wheel distribution:  python setup.py bdist_wheel


Distribute
==========
test repo: twine upload --repository-url https://test.pypi.org/legacy/ dist/*
prod repo: twine upload dist/*