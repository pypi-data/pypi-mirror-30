************
Context loop
************

:Info: Context loop.
:Author: Paweł Zadrożny @pawelzny <pawel.zny@gmail.com>


.. image:: https://circleci.com/gh/pawelzny/context-loop.svg?style=shield&circle-token=9dfb6c240de494af453a2899a7cf6d66c51aa723
   :target: https://circleci.com/gh/pawelzny/context-loop
   :alt: CI Status

.. image:: https://readthedocs.org/projects/context-loop/badge/?version=latest
   :target: http://context-loop.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/context-loop.svg
   :target: https://pypi.org/project/context-loop/
   :alt: PyPI Repository Status

.. image:: https://img.shields.io/github/release/pawelzny/context-loop.svg
   :target: https://github.com/pawelzny/context-loop
   :alt: Release Status

.. image:: https://img.shields.io/pypi/status/context-loop.svg
   :target: https://pypi.org/project/context-loop/
   :alt: Project Status

.. image:: https://img.shields.io/pypi/pyversions/context-loop.svg
   :target: https://pypi.org/project/context-loop/
   :alt: Supported python versions

.. image:: https://img.shields.io/pypi/implementation/context-loop.svg
   :target: https://pypi.org/project/context-loop/
   :alt: Supported interpreters

.. image:: https://img.shields.io/pypi/l/context-loop.svg
   :target: https://github.com/pawelzny/context-loop/blob/master/LICENSE
   :alt: License


Features
========

* Work with sync and async frameworks
* Schedule tasks to existing loop or create new one
* No need to understand how async works
* No callbacks required
* Run async tasks whenever and wherever you want


Installation
============

.. code:: bash

    pip install context-loop


**Package**: https://pypi.org/project/context-loop/


Documentation
=============

Read full documentation at http://context-loop.readthedocs.io/en/stable/


Quick Example
=============

.. code:: python

    >>> async def coro():
    ...     return await something_from_future()
    ...
    >>> import cl.Loop
    >>> with cl.Loop(coro(), coro(), coro()) as loop:
    ...    result = loop.run_until_complete()
    ...
    >>> result
    ['success', 'success', 'success']
