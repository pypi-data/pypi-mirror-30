=========================
Flake8 super call Checker
=========================

``flake8-super-call`` is a `Flake8 <http://flake8.pycqa.org/>`_ extension that
checks Python methods for anti-pattern ``super`` calls.

When calling ``super`` in a derived class, passing ``self.__class__`` to ``super()`` can give the wrong starting point
to search for methods, and will end up calling its own method again. More details on this `Stack Overflow question`__.

__ https://stackoverflow.com/questions/18208683/when-calling-super-in-a-derived-class-can-i-pass-in-self-class


Installation
------------

Install from PyPI using ``pip``:

.. code-block:: sh

    $ pip install flake8-super-call

The extension will be activated automatically by ``flake8``. You can verify
that it has been loaded by inspecting the ``flake8 --version``:

.. code-block:: sh

    $ flake8 --version
    3.5.0 (flake8_super_call: 1.0.0, mccabe: 0.6.1, pycodestyle: 2.3.1, pyflakes: 1.6.0) CPython 2.7.10 on Darwin


Error Codes
-----------

This extension adds one new `error code`_:

- ``S777``: Cannot use ``self.__class__`` as first argument of ``super()`` call

.. _error code: http://flake8.pycqa.org/en/latest/user/error-codes.html
