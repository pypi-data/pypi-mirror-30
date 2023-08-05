# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import sys

import pytest
from celery import Celery, shared_task
from flask import Flask


@pytest.yield_fixture()
def app(request):
    """Flask app fixture."""
    app = Flask("testapp")
    app.config.update(dict(
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True
    ))

    @shared_task
    def shared_compute():
        """Dummy function."""
        pass

    yield app

    import celery._state
    celery._state._apps.discard(
        app.extensions['invenio-celery'].celery._get_current_object()
    )
    celery._state._on_app_finalizers = set()
    celery._state.set_default_app(Celery())

    # Clear our modules to get them re-imported by Celery.
    if 'first_tasks' in sys.modules:
        del sys.modules['first_tasks']
    if 'second_tasks' in sys.modules:
        del sys.modules['second_tasks']
