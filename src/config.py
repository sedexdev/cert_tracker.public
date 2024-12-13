"""
Development config class
"""

# pylint: disable=too-few-public-methods

import os


class Config:
    """
    Sets local env variables for the app
    """
    FLASK_ENV = os.environ["FLASK_ENV"]
    FLASK_APP = os.environ["FLASK_APP"]
    FLASK_DEBUG = os.environ["FLASK_DEBUG"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
