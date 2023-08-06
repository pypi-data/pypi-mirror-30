=============================
Django Curated Literature Knowledge Base
=============================

.. image:: https://badge.fury.io/py/django-literature-knowledgebase.svg
    :target: https://badge.fury.io/py/django-literature-knowledgebase

.. image:: https://travis-ci.org/chopdgd/django-literature-knowledgebase.svg?branch=develop
    :target: https://travis-ci.org/chopdgd/django-literature-knowledgebase

.. image:: https://codecov.io/gh/chopdgd/django-literature-knowledgebase/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/chopdgd/django-literature-knowledgebase

.. image:: https://pyup.io/repos/github/chopdgd/django-literature-knowledgebase/shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-literature-knowledgebase/
    :alt: Updates

.. image:: https://pyup.io/repos/github/chopdgd/django-literature-knowledgebase/python-3-shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-literature-knowledgebase/
    :alt: Python 3

Django app for creating a knowledge base of curated literature

Documentation
-------------

The full documentation is at https://django-literature-knowledgebase.readthedocs.io.

Quickstart
----------

Install Django Curated Literature Knowledge Base::

    pip install django-literature-knowledgebase

Add it to your `INSTALLED_APPS` (along with DRF and django-filters):

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'django_filters',
        ...
        'literature_knowledgebase',
        'user_activities',
        ...
    )

Add Django Curated Literature Knowledge Base's URL patterns:

.. code-block:: python

    from literature_knowledgebase import urls as literature_knowledgebase_urls


    urlpatterns = [
        ...
        url(r'^', include(literature_knowledgebase_urls, namespace='literature_knowledgebase')),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
