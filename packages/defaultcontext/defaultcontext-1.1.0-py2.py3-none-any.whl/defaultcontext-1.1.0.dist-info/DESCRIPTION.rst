**************
defaultcontext
**************

.. image:: https://badge.fury.io/py/defaultcontext.svg
   :target: https://badge.fury.io/py/defaultcontext
.. image:: https://travis-ci.org/bogdan-kulynych/defaultcontext.svg?branch=master
   :target: https://travis-ci.org/bogdan-kulynych/defaultcontext

Tiny util for creating `tensorflow`_-like context managers for default instances of classes.


Installation
============

You can install ``defaultcontext`` using pip::

    pip install defaultcontext


Usage
=====

The library provides the ``with_default_context`` class decorator which simply does two things:

- Adds static method ``Class.get_default()`` which returns the default object in the current context block.
- Adds method ``instance.as_default()`` to the class, which manages a context within which the ``instance``
  becomes default

This is useful for creating psuedo-global objects that can be accessed from any code executed within a
given context block without passing such objects around.

This idea is inspired by ``Graph`` and ``Session`` classes from Google's `tensorflow`_.

Basic usage:

.. code-block::  python

    from defaultcontext import with_default_context


    @with_default_context
    class Environment:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return 'Environment %s' % self.name


    with Environment(name='A').as_default():
        print(Environment.get_default())      # A

    with Environment(name='B').as_default():
        print(Environment.get_default())      # B

    print(Environment.get_default())          # None

If ``with_default_context`` was called without parameters the global default value of a class will be ``None``.
The global default can be added using ``global_default_factory``:

.. code-block::  python

    def make_default_env():
        return Environment(name='default')

    @with_default_context(global_default_factory=make_default_env)
    class Environment:
        def __init__(self, name):
            self.name = name

        def __str__(self):
            return self.name

    Environment.get_default()                      # default

    with Environment(name='custom').as_default():
        print(Environment.get_default())           # custom

    Environment.get_default()                      # default

Alternatively, if the class can be constructed without arguments, global default can be set to ``Class()`` by
setting ``use_empty_init`` to ``True``:

.. code-block::  python

    @with_default_context(use_empty_init=True)
    class Environment:
        def __init__(self, name='default'):
            self.name = name

        def __str__(self):
            return self.name

    Environment.get_default()                      # default

    with Environment(name='custom').as_default():
        print(Environment.get_default())           # custom

    Environment.get_default()                      # default


.. _tensorflow: https://www.tensorflow.org/



