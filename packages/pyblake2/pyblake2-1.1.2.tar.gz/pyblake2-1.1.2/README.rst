pyblake2 — BLAKE2 hash function for Python
==========================================

.. image:: https://travis-ci.org/dchest/pyblake2.svg
   :alt: Build status

pyblake2 is an extension module for Python implementing BLAKE2 hash function.

  **NOTE:** Python 3.6 and later have native support for
  `BLAKE2 in hashlib <https://docs.python.org/3.6/library/hashlib.html? highlight=hashlib#hashlib.blake2b>`_
  derived from this implementation, with compatible API.
  This module should only be used if you want BLAKE2 in
  older Python versions, such as 2.7 or 3.5 and earlier.
  This module will have bug fixes for as long as possible,
  but no major code changes are planned.

BLAKE2 is a cryptographic hash function, which offers highest security while
being as fast as MD5 or SHA-1, and comes in two flavors:

* BLAKE2b, optimized for 64-bit platforms and produces digests of any size
  between 1 and 64 bytes,

* BLAKE2s, optimized for 8- to 32-bit platforms and produces digests of any
  size between 1 and 32 bytes.

BLAKE2 supports keyed mode (a faster and simpler replacement for HMAC),
salted hashing, personalization, and tree hashing.

Hash objects from this module follow the API of standard library's
`hashlib` objects.


Installation
------------

From PyPI::

    $ pip install pyblake2

or download source code and run::

    $ python setup.py install


Usage
-----

See documentation: http://pythonhosted.org/pyblake2/



