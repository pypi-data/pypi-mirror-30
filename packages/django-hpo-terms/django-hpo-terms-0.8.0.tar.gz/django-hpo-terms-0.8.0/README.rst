=============================
Django HPO Terms
=============================

.. image:: https://badge.fury.io/py/django-hpo-terms.svg
    :target: https://badge.fury.io/py/django-hpo-terms

.. image:: https://travis-ci.org/chopdgd/django-hpo-terms.svg?branch=develop
    :target: https://travis-ci.org/chopdgd/django-hpo-terms

.. image:: https://codecov.io/gh/chopdgd/django-hpo-terms/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/chopdgd/django-hpo-terms

.. image:: https://pyup.io/repos/github/chopdgd/django-hpo-terms/shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-hpo-terms/
    :alt: Updates

.. image:: https://pyup.io/repos/github/chopdgd/django-hpo-terms/python-3-shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-hpo-terms/
    :alt: Python 3

Django app to parse, store, and update HPO terms

Documentation
-------------

The full documentation is at https://django-hpo-terms.readthedocs.io.

Quickstart
----------

Install Django HPO Terms::

    pip install django-hpo-terms

Add it to your `INSTALLED_APPS` (along with DRF and django-filters):

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'django_filters',
        ...
        'hpo_terms',
        'genome',
        ...
    )

Add Django HPO Terms's URL patterns:

.. code-block:: python

    from hpo_terms import urls as hpo_terms_urls


    urlpatterns = [
        ...
        url(r'^', include(hpo_terms_urls, namespace='hpo_terms')),
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
