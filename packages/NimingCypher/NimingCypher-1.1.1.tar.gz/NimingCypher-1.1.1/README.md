Niming Cypher
=============

High security encryption module for instant messaging

==================
Getting Started
==================

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

-------------
Prerequisites
-------------

What things you need to install the software and how to install them

.. code:: shell

	$ pip install beautifulsoup4

----------
Installing
----------

This is the way to install Niming Crypter

.. code:: shell

	$ pip install NimingCrypter

Now you know the way !

=====
Usage
=====

----------------
Encrypt a string
----------------

Tested with python 3.6

.. code:: python
	import NimingCypher as nc
	crypter = nc.NCrypter("https://key.com")
	encrypted_str = crypter.CryptText("simple string")
	print(encrypted_str)

==========
Built With
==========

* `BeautifulSoup<https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_ - Parsing module

======
Author
======

* **Gissinger Arnaud** - *also known as Mathix*

=======
Licence
=======

This project is licensed under the MIT License - see the `LICENCE.txt<LICENCE.txt>`_ file for details