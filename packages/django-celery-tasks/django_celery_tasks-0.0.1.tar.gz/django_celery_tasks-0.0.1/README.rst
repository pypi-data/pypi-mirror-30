=====================================================================
 Task management in Django using Celery Result Backends as base.
=====================================================================

|build-status|

:Version: 0.0.1
:Download: http://pypi.python.org/pypi/django-celery-tasks
:Source: http://github.com/sbneto/django-celery-tasks
:Keywords: django, celery, database, results

About
=====

This extension builds upon the django-celery-results extension allowing to store relevant
tasks information in a Django model, as well as display and manage tasks more efficiently.

This is a work in progresss at the moment.

Installation
============

You can install django-celery-tasks either via the Python Package Index (PyPI)
or from source.

To install using `pip`::

    $ pip install -U django-celery-tasks

.. _installing-from-git:

Using the development version
-----------------------------

With pip
~~~~~~~~

You can install the latest snapshot of django-celery-tasks using the following
pip command::

    $ pip install https://github.com/celery/django-celery-tasks/zipball/master#egg=django-celery-tasks

.. |build-status| image:: https://secure.travis-ci.org/sbneto/django-celery-tasks.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/celery/django-celery-tasks
