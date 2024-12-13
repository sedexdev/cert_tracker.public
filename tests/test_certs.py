"""
Cert operations test module
"""

# pylint: disable=duplicate-code, line-too-long, too-many-public-methods

from flask import Flask
from flask.testing import FlaskClient

from src.db import db
from src.models.cert import Cert


class TestCerts:
    """
    Cert creation and management test class. Includes case for 
    all composite classes of Cert (Video/Article/Course etc) 
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.form_data = None

    def setup_method(self) -> None:
        """
        Setup class before all tests run
        """
        # create new cert from form
        self.form_data = {
            "name": "Test",
            "code": "tst-101",
            "date": "01/01/2000",
            "head_img": "test/test.jpg",
            "badge_img": "etest/BADGE_test.png",
            "exam_date": "",
            "tags": "test_tag",
        }

    # ===== find() =====

    def test_find_returns_test_cert_from_code(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert find() search query 'tst-101' returns the test cert in a list 

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.form_data)
        with app.app_context():
            result = Cert.find("tst-101")
        assert isinstance(result, list) and result[0].name == "Test"

    def test_find_returns_test_cert_from_name(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert find() search query 'Test' returns the test cert in a list 

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.form_data)
        with app.app_context():
            db.session.commit()
            result = Cert.find("Test")
        assert isinstance(result, list) and result[0].name == "Test"

    def test_find_returns_test_cert_from_tag(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert find() search query 'test_tag' returns the test cert in a list 

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.form_data)
        with app.app_context():
            db.session.commit()
            result = Cert.find("test_tag")
        assert isinstance(result, list) and result[0].name == "Test"

    # ===== /create/cert =====

    def test_create_new_creates_object(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert create_new() creates a new Cert and updates database

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.form_data)
        with app.app_context():
            cert = Cert.query.filter_by(name=self.form_data["name"]).first()
        assert cert is not None and cert.name == "Test"

    def test_create_new_redirects(self, client: FlaskClient) -> None:
        """
        Assert create_new() creates a new Cert and redirects user

        Args:
            client (FlaskClient): Flask app test client
        """
        response = client.post("/create/cert", data=self.form_data)
        assert response.status_code == 302

    def test_create_new_returns_form_if_not_valid(self, client: FlaskClient) -> None:
        """
        Assert create_new() returns the form if form invalid

        Args:
            client (FlaskClient): Flask app test client
        """
        response = client.post("/create/cert", data={})
        assert b"Create new cert" in response.data
