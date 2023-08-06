.. -*- coding: utf-8 -*-
.. :Project:   python-rapidjson -- Introduction
.. :Author:    Ken Robbins <ken@kenrobbins.com>
.. :License:   MIT License
.. :Copyright: © 2015 Ken Robbins
.. :Copyright: © 2016, 2017, 2018 Lele Gaifax
..

==================
 python-rapidjson
==================

Python wrapper around RapidJSON
===============================

 :Authors: Ken Robbins <ken@kenrobbins.com>; Lele Gaifax <lele@metapensiero.it>
 :License: `MIT License`__
 :Status: |build| |doc|

__ https://raw.githubusercontent.com/python-rapidjson/python-rapidjson/master/LICENSE
.. |build| image:: https://travis-ci.org/python-rapidjson/python-rapidjson.svg?branch=master
   :target: https://travis-ci.org/python-rapidjson/python-rapidjson
   :alt: Build status
.. |doc| image:: https://readthedocs.org/projects/python-rapidjson/badge/?version=latest
   :target: https://readthedocs.org/projects/python-rapidjson/builds/
   :alt: Documentation status

RapidJSON_ is an extremely fast C++ JSON parser and serialization library: this module
wraps it into a Python 3 extension, exposing its serialization/deserialization (to/from
either ``bytes``, ``str`` or *file-like* instances) and `JSON Schema`__ validation
capabilities.

Latest version documentation is automatically rendered by `Read the Docs`__.

__ http://json-schema.org/documentation.html
__ http://python-rapidjson.readthedocs.io/en/latest/


Getting Started
---------------

First install ``python-rapidjson``:

.. code-block:: bash

    $ pip install python-rapidjson

or, if you prefer `Conda`__:

.. code-block:: bash

    $ conda install -c conda-forge python-rapidjson

__ https://conda.io/docs/

Basic usage looks like this:

.. code-block:: python

    >>> import rapidjson
    >>> data = {'foo': 100, 'bar': 'baz'}
    >>> rapidjson.dumps(data)
    '{"bar":"baz","foo":100}'
    >>> rapidjson.loads('{"bar":"baz","foo":100}')
    {'bar': 'baz', 'foo': 100}
    >>>
    >>> class Stream:
    ...   def write(self, data):
    ...      print("Chunk:", data)
    ...
    >>> rapidjson.dump(data, Stream(), chunk_size=5)
    Chunk: b'{"foo'
    Chunk: b'":100'
    Chunk: b',"bar'
    Chunk: b'":"ba'
    Chunk: b'z"}'


Development
-----------

If you want to install the development version (maybe to contribute fixes or
enhancements) you may clone the repository:

.. code-block:: bash

    $ git clone --recursive https://github.com/python-rapidjson/python-rapidjson.git

.. note:: The ``--recursive`` option is needed because we use a *submodule* to
          include RapidJSON_ sources. Alternatively you can do a plain
          ``clone`` immediately followed by a ``git submodule update --init``.

          Alternatively, if you already have (a *compatible* version of)
          RapidJSON includes around, you can compile the module specifying
          their location with the option ``--rj-include-dir``, for example:

          .. code-block:: shell

             $ python3 setup.py build --rj-include-dir=/usr/include/rapidjson

A set of makefiles implement most common operations, such as *build*, *check*
and *release*; see ``make help`` output for a list of available targets.


Performance
-----------

``python-rapidjson`` tries to be as performant as possible while staying
compatible with the ``json`` module.

The following tables show a comparison between this module and other libraries
with different data sets.  Last row (“overall”) is the total time taken by all
the benchmarks.

Each number shows the factor between the time taken by each contender and
``python-rapidjson`` (in other words, they are *normalized* against a value of
1.0 for ``python-rapidjson``): the lower the number, the speedier the
contender.

In **bold** the winner.


Serialization
~~~~~~~~~~~~~

+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|       serialize       |  ``dumps()``\ [1]_   | ``Encoder()``\ [2]_  |  ``dumps(n)``\ [3]_  | ``Encoder(n)``\ [4]_ |     ujson\ [5]_      |   simplejson\ [6]_   |     stdlib\ [7]_     |      yajl\ [8]_      |
+=======================+======================+======================+======================+======================+======================+======================+======================+======================+
|    100 arrays dict    |         1.00         |         0.97         |         0.75         |       **0.75**       |         0.92         |         4.15         |         2.16         |         1.29         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|    100 dicts array    |         1.00         |         1.04         |         0.84         |       **0.82**       |         1.08         |         5.29         |         2.22         |         1.35         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|    256 Trues array    |       **1.00**       |         1.17         |         1.21         |         1.22         |         1.50         |         2.93         |         2.25         |         1.32         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|    256 ascii array    |         1.00         |         1.01         |         1.04         |         1.04         |       **0.52**       |         1.21         |         1.05         |         1.24         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|   256 doubles array   |       **1.00**       |         1.02         |         1.12         |         1.02         |         6.94         |         7.90         |         8.26         |         4.02         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|   256 unicode array   |         1.00         |         0.86         |         0.87         |         0.85         |         0.55         |         0.72         |         0.65         |       **0.52**       |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|    complex object     |         1.00         |         1.01         |       **0.85**       |         0.88         |         1.02         |         3.86         |         2.56         |         2.09         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|   composite object    |         1.00         |         1.02         |         0.73         |       **0.70**       |         0.87         |         2.79         |         1.83         |         1.88         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+
|        overall        |         1.00         |         0.97         |         0.75         |       **0.75**       |         0.92         |         4.14         |         2.16         |         1.29         |
+-----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+----------------------+


Deserialization
~~~~~~~~~~~~~~~

+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|      deserialize      |   ``loads()``\ [9]_   | ``Decoder()``\ [10]_  |  ``loads(n)``\ [11]_  | ``Decoder(n)``\ [12]_ |         ujson         |      simplejson       |        stdlib         |         yajl          |
+=======================+=======================+=======================+=======================+=======================+=======================+=======================+=======================+=======================+
|    100 arrays dict    |         1.00          |         1.00          |         0.90          |       **0.89**        |         0.96          |         1.52          |         1.17          |         1.14          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|    100 dicts array    |         1.00          |         1.22          |       **0.85**        |         0.87          |         0.93          |         2.13          |         1.58          |         1.23          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|    256 Trues array    |       **1.00**        |         1.37          |         1.19          |         1.24          |         1.12          |         2.04          |         1.77          |         1.77          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|    256 ascii array    |       **1.00**        |         1.03          |         1.03          |         1.04          |         1.38          |         1.22          |         1.17          |         1.41          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|   256 doubles array   |         1.00          |         0.96          |         0.26          |       **0.22**        |         0.50          |         1.06          |         0.99          |         0.52          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|   256 unicode array   |       **1.00**        |         1.01          |         1.02          |         1.01          |         1.26          |         5.35          |         6.05          |         2.96          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|    complex object     |         1.00          |         1.02          |         0.98          |       **0.84**        |         1.09          |         1.79          |         1.31          |         1.34          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|   composite object    |         1.00          |         1.03          |         0.80          |         0.83          |       **0.75**        |         2.01          |         1.36          |         1.22          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+
|        overall        |         1.00          |         1.00          |         0.90          |       **0.89**        |         0.96          |         1.52          |         1.18          |         1.14          |
+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+-----------------------+

.. [1] ``rapidjson.dumps()``
.. [2] ``rapidjson.Encoder()``
.. [3] ``rapidjson.dumps(number_mode=NM_NATIVE)``
.. [4] ``rapidjson.Encoder(number_mode=NM_NATIVE)``
.. [5] `ujson 1.35 <https://pypi.python.org/pypi/ujson/1.35>`__
.. [6] `simplejson 3.13.2 <https://pypi.python.org/pypi/simplejson/3.13.2>`__
.. [7] Python 3.6.4 standard library ``json``
.. [8] `yajl 0.3.5 <https://pypi.python.org/pypi/yajl/0.3.5>`__
.. [9] ``rapidjson.loads()``
.. [10] ``rapidjson.Decoder()``
.. [11] ``rapidjson.loads(number_mode=NM_NATIVE)``
.. [12] ``rapidjson.Decoder(number_mode=NM_NATIVE)``


DIY
~~~

To run these tests yourself, clone the repo and run:

.. code-block:: bash

   $ make benchmarks

or

.. code-block:: bash

   $ make benchmarks-other

The former will focus only on ``RapidJSON`` and is particularly handy coupled
with the `compare past runs`__ functionality of ``pytest-benchmark``:

.. code-block:: bash

   $ make benchmarks PYTEST_OPTIONS=--benchmark-autosave
   # hack, hack, hack!
   $ make benchmarks PYTEST_OPTIONS=--benchmark-compare=0001

   ----------------------- benchmark 'deserialize': 18 tests ------------------------
   Name (time in us)                                                            Min…
   ----------------------------------------------------------------------------------
   test_loads[rapidjson-256 Trues array] (NOW)                         5.2320 (1.0)…
   test_loads[rapidjson-256 Trues array] (0001)                        5.4180 (1.04)…
   …

To reproduce the tables above run ``make benchmarks-tables``

__ http://pytest-benchmark.readthedocs.org/en/latest/comparing.html


Incompatibility
---------------

Here are things in the standard ``json`` library supports that we have decided
not to support:

``separators`` argument
  This is mostly used for pretty printing and not supported by ``RapidJSON``
  so it isn't a high priority. We do support ``indent`` kwarg that would get
  you nice looking JSON anyways.

Coercing keys when dumping
  ``json`` will stringify a ``True`` dictionary key as ``"true"`` if you dump it out but
  when you load it back in it'll still be a string. We want the dump and load to return
  the exact same objects so we have decided not to do this coercion.

Arbitrary encodings
  ``json.loads()`` accepts an ``encoding`` kwarg determining the encoding of its input,
  when that is a ``bytes`` or ``bytearray`` instance. Although ``RapidJSON`` is able to
  cope with several different encodings, we currently supports only the recommended one,
  ``UTF-8``.

.. _RapidJSON: http://rapidjson.org/
