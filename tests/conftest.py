"""
Pytest configuration module
"""

# pylint: disable=redefined-outer-name

import pytest

from flask import Flask
from flask.testing import FlaskClient

from src import create_app
from src.db import db
from src.models.cert import Cert
from src.models.resource import Resource
from src.models.section import Section


@pytest.fixture()
def app():
    """
    Yields an instance of the Flask app

    Yields:
        Flask: app instance
    """
    application = create_app()
    application.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    yield application


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    """
    Gets a test client from the test Flask instance

    Args:
        app (Flask): Flask app instance

    Returns:
        FlaskClient: test client
    """
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app: Flask):
    """
    Cleans the test db after each test

    Args:
        app (Flask): Flask app instance
    """
    with app.app_context():
        Cert.query.delete()
        Resource.query.delete()
        Section.query.delete()
        db.session.commit()
