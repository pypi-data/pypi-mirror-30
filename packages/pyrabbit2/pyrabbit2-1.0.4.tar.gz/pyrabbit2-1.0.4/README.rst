
PyRabbit2
-------------------

.. image:: https://travis-ci.org/deslum/pyrabbit2.svg?branch=master
        :target: https://travis-ci.org/deslum/pyrabbit2
        
.. image:: https://img.shields.io/badge/python-2.x-yellow.svg
        :target: https://pypi.python.org/pypi/pyrabbit2/
        
.. image:: https://img.shields.io/badge/python-3.x-orange.svg
        :target: https://pypi.python.org/pypi/pyrabbit2/

.. image:: https://img.shields.io/badge/license-New%20BSD-blue.svg   
        :target: https://raw.githubusercontent.com/deslum/pyrabbit2/master/LICENSE

This project is fork project pyrabbit https://github.com/bkjones/pyrabbit 

I fork project, because he don't update many years.

Pyrabbit2 is a module to make it easy to interface w/ RabbitMQ's HTTP Management
API.  It's tested against RabbitMQ 3.7.4 using Python 2.7-3.6. It has
a pretty solid set of tests, and I use tox to test across Python versions.

PyRabbit2 is on PyPI, which makes it installable using pip or easy_install.

Features:
----------

* Users (Create, Read, Update, Delete)
* User acess SHA256 + salt 
* Permissions
* Polices
* Support SSL
* Vhosts (Create, Read, Update, Delete)
* Exchanges (Create, Read, Update, Delete)
* Bindings (Create, Read, Update, Delete)
* Queues (Create, Read, Update, Delete)
* Shovel
* Work with cluster nodes
* Many features support RabbitMQ API https://pulse.mozilla.org/api/

Install
-----------
::

     pip3 install pyrabbit2
     

Documentation
--------------
     
http://pyrabbit.readthedocs.org
