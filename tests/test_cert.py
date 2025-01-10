"""
Cert operations test module
"""

# pylint: disable=duplicate-code

import json
import os

from pathlib import Path

import requests

from flask import Flask
from flask.testing import FlaskClient

from src.models.cert import Cert
from src.db import db

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}"
    )
)

CERT_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/tst101")


class TestCerts:
    """
    Cert creation and management test class
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.cert_data = None

    def setup_method(self) -> None:
        """
        Setup class before all tests run
        """
        # create new cert from form
        self.cert_data = {
            "name": "Test",
            "code": "tst-101",
            "date": "01/01/2000",
            "head_img": "tests/images/test.jpg",
            "badge_img": "tests/images/BADGE_test.png",
            "exam_date": None,
            "reminder": False,
            "cost": None,
            "tags": "test_tag",
        }

    def teardown_method(self) -> None:
        """
        Teardown methods after each test runs
        """
        test_name = os.environ \
            .get('PYTEST_CURRENT_TEST') \
            .split(':')[-1] \
            .split(' ')[0]
        # only run on tests that update the json data file
        tests = [
            "test_content_update_cert_exam_reminder_updates_json_file",
            "test_content_update_cert_exam_reminder_deletes_reminder",
        ]
        if test_name in tests:
            with open(f"{PROJECT_ROOT}/tests/test_data.json", "r+", encoding="utf-8") as file:
                data = json.loads(file.read())
                # delete the test data
                try:
                    del data["tst101"]
                except KeyError:
                    pass
                file.seek(0)
                file.truncate()
                file.write(json.dumps(data))
        # remove test cert image directory
        if CERT_PATH.exists():
            for file in CERT_PATH.iterdir():
                file.unlink()
            CERT_PATH.rmdir()

    # ===== find() =====

    def test_find_returns_test_cert_from_code(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert find() search query 'tst-101' returns the test cert in a list 

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert
        client.post("/create/cert", data=self.cert_data)
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
        # create cert
        client.post("/create/cert", data=self.cert_data)
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
        # create cert
        client.post("/create/cert", data=self.cert_data)
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
        # create cert
        client.post("/create/cert", data=self.cert_data)
        with app.app_context():
            cert = Cert.query.filter_by(name=self.cert_data["name"]).first()
        assert cert is not None and cert.name == "Test"

    def test_create_new_redirects(self, client: FlaskClient) -> None:
        """
        Assert create_new() creates a new Cert and redirects user

        Args:
            client (FlaskClient): Flask app test client
        """
        # create cert
        response = client.post("/create/cert", data=self.cert_data)
        assert response.status_code == 302

    def test_create_new_returns_form_if_not_valid(self, client: FlaskClient) -> None:
        """
        Assert create_new() returns the form if form invalid

        Args:
            client (FlaskClient): Flask app test client
        """
        response = client.post("/create/cert", data={})
        assert b"Create new cert" in response.data

    def test_content_create_fails_unique_constraint_name(self, client: FlaskClient) -> None:
        """
        Assert Cert not created if a unique constraint on the cert name

        Args:
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.cert_data)
        response = client.post("/create/cert", data=self.cert_data)
        assert \
            response.status_code == 200 and \
            b"Create new cert" in response.data

    def test_content_create_fails_unique_constraint_code(self, client: FlaskClient) -> None:
        """
        Assert Cert not created if a unique constraint on the cert code

        Args:
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.cert_data)
        # change name for check for code
        self.cert_data["name"] = "Another Test"
        response = client.post("/create/cert", data=self.cert_data)
        assert \
            response.status_code == 200 and \
            b"Create new cert" in response.data

        # ===== /update/cert/<int:cert_id> =====

    def test_update_cert(self, client: FlaskClient) -> None:
        """
        Asserts that a Cert object is updated in the DB

        Args:
            client (FlaskClient): Flask app test client
        """
        client.post("/create/cert", data=self.cert_data)
        # update the cert
        self.cert_data["name"] = "Updated test"
        client.post("/update/cert/1", data=self.cert_data)
        # get the cert data
        response = requests.get(f"{API_URL}/cert/1", timeout=2)
        data = response.json()
        # assert updates were saved
        assert data["name"] == "Updated test"

    def test_update_cert_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts that a 404 response is returned if Cert not found

        Args:
            client (FlaskClient): Flask app test client
        """
        # update a cert that doesn't exist
        self.cert_data["name"] = "Updated test"
        client.post("/update/cert/1", data=self.cert_data)
        # test for error response
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "Cert not found") in flashes

    # ===== /update/cert/exam_date =====

    def test_content_update_cert_exam_date_formats_correctly(self, client: FlaskClient) -> None:
        """
        Assert updating an exam date saves in the correct UK
        format e.g. 

        30th Nov 2024 -> 30/11/2024

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response = requests.get(url=f"{API_URL}/cert/1", timeout=2)
        data = response.json()
        data["cert_id"] = 1
        data["exam-date"] = "2024-11-30"
        client.post("/update/cert/exam_date", data=data)
        response = requests.get(f"{API_URL}/cert/1", timeout=2)
        data = response.json()
        assert data["exam_date"] == "30/11/2024"

    def test_content_update_cert_exam_date_empty_date(self, client: FlaskClient) -> None:
        """
        Assert trying to update date with empty string 
        flashes error

        Args:
            client (FlaskClient): Flask app test client
        """
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response = requests.get(url=f"{API_URL}/cert/1", timeout=2)
        data = response.json()
        data["cert_id"] = 1
        data["exam-date"] = ""
        response = client.post("/update/cert/exam_date", data=data)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("error", "Please provide a valid date") in flashes

    # ===== /update/cert/exam_reminder

    def test_content_update_cert_exam_reminder_updates_json_file(self, client: FlaskClient) -> None:
        """
        Assert that the test_data.json file is correctly updated

        Args:
            client (FlaskClient): Flask app test client
        """
        # create cert as required for reminder details
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # update the exam date
        client.post("/update/cert/exam_date", data={
            "cert_id": 1,
            "exam-date": "01/01/2025",
        })
        # set reminder
        form_data = {
            "cert_id": 1,
            "frequency": "weekly",
            "starting_from": "2025-01-01",
            "testing": True  # target the test_data.json file
        }
        client.post("/update/cert/exam_reminder", data=form_data)
        # read test_data.json to assert values are written
        with open(f"{PROJECT_ROOT}/tests/test_data.json", "r", encoding="utf-8") as file:
            data = json.loads(file.read())
        assert \
            data["tst101"]["name"] == "Test" and \
            data["tst101"]["code"] == "tst-101"

    def test_content_update_cert_exam_reminder_deletes_reminder(self, client: FlaskClient) -> None:
        """
        Assert a cert entry is removed from the data file

        Args:
            client (FlaskClient): Flask app test client
        """
        # create cert as required for reminder details
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # update the exam date
        client.post("/update/cert/exam_date", data={
            "cert_id": 1,
            "exam-date": "01/01/2025",
        })
        # add the cert
        form_data = {
            "cert_id": 1,
            "frequency": "weekly",
            "starting_from": "2025-01-01",
            "testing": True  # target the test_data.json file
        }
        client.post("/update/cert/exam_reminder", data=form_data)
        # then delete the entry
        form_data = {
            "cert_id": 1,
            "starting_from": "2025-01-01",  # date required
            "testing": True,  # target the test_data.json file
            "delete": True,  # state this is a delete op
        }
        response = client.post("/update/cert/exam_reminder", data=form_data)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        # assert the entry has been removed
        with open(f"{PROJECT_ROOT}/tests/test_data.json", "r+", encoding="utf-8") as file:
            data = json.loads(file.read())
        assert \
            response.status_code == 302 and \
            ("message", "Email reminder deleted") in flashes and \
            data.get("tst101") is None

    def test_content_update_cert_exam_reminder_empty_date(self, client: FlaskClient) -> None:
        """
        Assert

        Args:
            client (FlaskClient): Flask app test client
        """
        # create cert as required for reminder details
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        form_data = {
            "cert_id": 1,
            "frequency": "weekly",
            "starting_from": ""
        }
        response = client.post("/update/cert/exam_reminder", data=form_data)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("error", "Please provide a valid date") in flashes
