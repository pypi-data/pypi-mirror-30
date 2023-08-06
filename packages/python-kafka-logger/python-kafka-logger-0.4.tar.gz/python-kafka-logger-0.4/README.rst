===============================
Python Kafka Logging Handler
===============================

.. image:: https://img.shields.io/pypi/d/python-kafka-logger.svg
    :target: https://pypi.python.org/pypi/python-kafka-logger/
    :alt: Downloads
.. image:: https://img.shields.io/pypi/v/python-kafka-logger.svg
    :target: https://pypi.python.org/pypi/python-kafka-logger/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/l/python-kafka-logger.svg
    :target: https://pypi.python.org/pypi/python-kafka-logger/
    :alt: License

Simple python logging handler for forwarding logs to a kafka server.

The handler uses a logstash formatter.


Installing
==========

.. code-block:: shell

	$ pip install python-kafka-logger


How to use 
==========
Example for using the handler within a native logging.conf file

.. code-block:: shell

	example/logging.conf
   


Get the project
===============

	1. Clone the git repository
	
	.. code-block:: shell
	
		$ git clone https://github.com/avihoo/python-kafka-logging/

	2. Install a virtualenv
	
	.. code-block:: shell
	
		$ sudo apt-get install python-virtualenv

	3. Create a new virtualenv
	
	.. code-block:: shell
	
		$ virtualenv python-kafka-logging-ve

	4. Install project's requirements
	
	.. code-block:: shell
	
		$ python-kafka-logging-ve/bin/pip install -r requirements.txt



Reporting Issues
================
If you have suggestions, bugs or other issues specific to this library, file them `here`_ or contact me at avihoo.mamka <at> gmail <dot> com.



keywords: python, logging, handler, example, kafka, logs, logstash, formatter

.. _here: https://github.com/avihoo/python-kafka-logging/issues

