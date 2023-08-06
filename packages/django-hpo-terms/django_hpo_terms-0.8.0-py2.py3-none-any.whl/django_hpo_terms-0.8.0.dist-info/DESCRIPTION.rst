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




History
-------

0.1.0 (2017-12-29)
++++++++++++++++++

* First release on PyPI.
* Initial models and REST API.

0.2.0 (2017-12-31)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.1.0...v0.2.0>`_

* Added syncing of database with online HPO resources.

0.3.0 (2017-01-02)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.2.0...v0.3.0>`_

* Added Disease genes model and REST API.
* Synced Disease genes from online HPO resource.

0.3.1 (2017-01-04)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.3.0...v0.3.1>`_

* Fixed minor bugs
* Added better test coverage for hpo_sync.

0.4.0 (2017-01-05)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.3.1...v0.4.0>`_

* Improved REST API filters.

0.4.1 (2017-01-09)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.4.0...v0.4.1>`_

* Fixed issues with migrations.

0.4.2 (2017-01-12)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.4.1...v0.4.2>`_

* Fixed route names for SimpleRouter.

0.5.0 (2017-02-09)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.4.2...v0.5.0>`_

* Add gene symbol filter for diseases API
* Added HPO term label to disease API
* updated requirements to the latest


0.6.0 (2017-03-30)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.5.0...v0.6.0>`_

* updated some dependencies

0.7.0 (2017-04-04)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.6.0...v0.7.0>`_

* Added support for GraphQL

0.8.0 (2017-04-07)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-hpo-terms/compare/v0.7.0...v0.8.0>`_

* Added support for Django 2.0 and Python 3.6
* Dropped support for Django < 1.11 and Python 2.7, 3.3, 3.4


