..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

================
 Invenio-Celery
================

.. image:: https://img.shields.io/travis/inveniosoftware/invenio-celery.svg
        :target: https://travis-ci.org/inveniosoftware/invenio-celery

.. image:: https://img.shields.io/coveralls/inveniosoftware/invenio-celery.svg
        :target: https://coveralls.io/r/inveniosoftware/invenio-celery

.. image:: https://img.shields.io/pypi/v/invenio-celery.svg
        :target: https://pypi.org/pypi/invenio-celery


Celery distributed task queue module for Invenio.

Invenio-Celery is a small discovery layer that takes care of discovering and
loading tasks from other Invenio modules, as well as providing configuration
defaults for Celery usage in Invenio. Invenio-Celery relies on Flask-CeleryExt
for integrating Flask and Celery with application factories.

Further documentation is available on https://invenio-celery.readthedocs.io/
