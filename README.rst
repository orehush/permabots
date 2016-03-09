=============================
microbot
=============================
CI:

.. image:: https://travis-ci.org/jlmadurga/microbot.svg?branch=master
    :target: https://travis-ci.org/jlmadurga/microbot

.. image:: https://coveralls.io/repos/github/jlmadurga/microbot/badge.svg?branch=master 
	:target: https://coveralls.io/github/jlmadurga/microbot?branch=master
  
.. image:: https://requires.io/github/jlmadurga/microbot/requirements.svg?branch=master
     :target: https://requires.io/github/jlmadurga/microbot/requirements/?branch=master
     :alt: Requirements Status
     
PyPI:


.. image:: https://img.shields.io/pypi/v/microbot.svg
        :target: https://pypi.python.org/pypi/microbot

Docs:

.. image:: https://readthedocs.org/projects/microbot/badge/?version=latest
        :target: https://readthedocs.org/projects/microbot/?badge=latest
        :alt: Documentation Status


Connect telegram bots to your API. 

The idea is to use it as microservice to host messaging bots leaving the application model into current APIs. 

Documentation
-------------

The full documentation is at https://microbot.readthedocs.org.

Quickstart
----------

Install microbot::

    pip install microbot

Then use it in a project::

    import microbot

Features
--------

* Telegram bots
* Message handling definition with regex, as django urls.
* HTTP methods: GET/POST/PUT/DELETE
* Text responses and keyboards with Jinja2 templates
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



