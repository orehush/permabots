=============================
permabots
=============================
CI:

.. image:: https://travis-ci.org/jlmadurga/permabots.svg?branch=master
    :target: https://travis-ci.org/jlmadurga/permabots

.. image:: https://coveralls.io/repos/github/jlmadurga/permabots/badge.svg?branch=master 
	:target: https://coveralls.io/github/jlmadurga/permabots?branch=master
  
.. image:: https://requires.io/github/jlmadurga/permabots/requirements.svg?branch=master
     :target: https://requires.io/github/jlmadurga/permabots/requirements/?branch=master
     :alt: Requirements Status
     
PyPI:


.. image:: https://img.shields.io/pypi/v/permabots.svg
        :target: https://pypi.python.org/pypi/permabots

Docs:

.. image:: https://readthedocs.org/projects/permabots/badge/?version=latest
        :target: https://readthedocs.org/projects/permabots/?badge=latest
        :alt: Documentation Status


Connect instant messaging bots to your APIs. 

The idea is to use it as microservice to host messaging bots leaving the application model into current APIs. 

Documentation
-------------

The full documentation is at https://permabots.readthedocs.org.

Quickstart
----------

Install permabots::

    pip install permabots

Then use it in a project::

    import permabots

Features
--------

* Telegram, Kik and Facebook Messenger bots
* Message handling definition with regex, as django urls.
* HTTP methods: GET/POST/PUT/DELETE/PATCH
* Text responses and keyboards with Jinja2 templates
* Chat State handling
* Asynchronous processing of messages
* Media messages not supported



Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements/test.txt
    (myenv) $ make test
    (myenv) $ make test-all



