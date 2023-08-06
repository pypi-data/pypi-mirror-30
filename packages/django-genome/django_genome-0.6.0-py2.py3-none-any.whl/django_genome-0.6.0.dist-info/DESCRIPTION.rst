=============================
Django Genome
=============================

.. image:: https://badge.fury.io/py/django-genome.svg
    :target: https://badge.fury.io/py/django-genome

.. image:: https://travis-ci.org/chopdgd/django-genome.svg?branch=develop
    :target: https://travis-ci.org/chopdgd/django-genome

.. image:: https://codecov.io/gh/chopdgd/django-genome/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/chopdgd/django-genome

.. image:: https://pyup.io/repos/github/chopdgd/django-genome/shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-genome/
    :alt: Updates

.. image:: https://pyup.io/repos/github/chopdgd/django-genome/python-3-shield.svg
    :target: https://pyup.io/repos/github/chopdgd/django-genome/
    :alt: Python 3

Django app for syncing and storing human genome reference data

Documentation
-------------

The full documentation is at https://django-genome.readthedocs.io.

Quickstart
----------

Install Django Genome::

    pip install django-genome

Add it to your `INSTALLED_APPS` (along with DRF and django-filters):

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'rest_framework',
        'django_filters',
        ...
        'genome',
        ...
    )

Add Django Genome's URL patterns:

.. code-block:: python

    from genome import urls as genome_urls


    urlpatterns = [
        ...
        url(r'^', include(genome_urls, namespace='genome')),
        ...
    ]

Initial sync for genome models::

    python manage.py genome_sync

Features
--------

* Includes models for Genome, Chromosome, CytoBand, Gene, Transcript, and Exons
* Syncs data for hg18, hg19, hg38 from HGNC and UCSC

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

0.1.0 (2017-12-30)
++++++++++++++++++

* First release on PyPI.
* Initial models and REST API
* Syncs data from HGNC and UCSC to build database

0.2.0 (2018-01-05)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.1.0...v0.2.0>`_

* Improved REST API Filters
* made Chromosomes and Gene Symbols save as uppercase to maintain consistency


0.2.1 (2018-01-08)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.2.0...v0.2.1>`_

* Fixed issues with migrations

0.2.2 (2018-01-12)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.2.1...v0.2.2>`_

* Fixed route names for SimpleRouter

0.3.0 (2018-02-09)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.2.2...v0.3.0>`_

* Updated requirements to the latest


0.4.0 (2018-03-30)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.3.0...v0.4.0>`_

* Added API for chromosomes
* Changed gene_symbol from being unique

0.5.0 (2018-04-04)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.4.0...v0.5.0>`_

* Added GraphQL Nodes

0.6.0 (2018-04-07)
++++++++++++++++++

`Full Changelog <https://github.com/chopdgd/django-genome/compare/v0.5.0...v0.6.0>`_

* Added support for Django 2 and Python 3.6
* Dropped support for Django < 1.11 and Python 2.7, 3.3, 3.4


