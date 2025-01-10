"""
Object deletion operations test module
"""

# pylint: disable=duplicate-code

import json
import os

from pathlib import Path

import requests

from flask import Flask
from flask.testing import FlaskClient

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}"
    )
)

CERT_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/tst103")


class TestDelete:
    """
    Object deletion test class
    """
    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.cert_data = None
        cls.resource_data = None
        cls.section_data = None

    def setup_method(self) -> None:
        """
        Setup methods before each test runs
        """
        # create new cert from form
        self.cert_data = {
            "name": "Test",
            "code": "tst-103",
            "date": "01/01/2000",
            "head_img": "tests/images/test.jpg",
            "badge_img": "tests/images/BADGE_test.png",
            "exam_date": None,
            "reminder": False,
            "cost": None,
            "tags": "test",
        }
        # create a new resource on the cert
        self.resource_data = {
            "cert_id": 1,
            "resource_type": "course",
            "url": "http://test.test",
            "title": "Test Course",
            "description": "This is a test course",
            "site_name": "Test",
            "image": "tests/images/test.jpg",
            "site_logo": "tests/images/BADGE_test.png",
            "has_og_data": False,
            "complete": False,
        }
        # create a new section on a course
        self.section_data = {
            "cert_id": 1,
            "resource_id": 1,
            "number": 1,
            "title": "Test section",
            "cards_made": None,
            "complete": None,
        }

    def teardown_method(self) -> None:
        """
        Teardown methods after each test runs
        """
        # remove test cert image directory
        if CERT_PATH.exists():
            for file in CERT_PATH.iterdir():
                file.unlink()
            CERT_PATH.rmdir()

    # ===== /delete/<int:resource_id> =====

    def test_content_delete_cert(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert a Cert object is successfully delete from the DB

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create a cert
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # delete the cert
        with app.app_context():
            response = client.post("/delete/1", data={"type": "cert"})
        # assert delete error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("message", "Cert deleted successfully") in flashes

    def test_content_delete_cert_and_all_resources(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert a Cert object is successfully delete from the DB along
        with any resources with the same cert_id

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create a cert
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # create a resource
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # create a section
        requests.post(
            url=f"{API_URL}/section",
            data=json.dumps(self.section_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # delete the cert
        with app.app_context():
            response = client.post("/delete/1", data={"type": "cert"})
        # get the associated resources
        resources = requests.get(url=f"{API_URL}/resource", timeout=2)
        sections = requests.get(url=f"{API_URL}/section", timeout=2)
        resource_data = resources.json()
        section_data = sections.json()
        # assert delete error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("message", "Cert deleted successfully") in flashes and \
            len(resource_data) == 0 and \
            len(section_data) == 0

    def test_content_delete_resource(self, client: FlaskClient) -> None:
        """
        Assert a Resource object is successfully delete from the DB

        Args:
            client (FlaskClient): Flask app test client
        """
        # create a resource
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # delete the resource
        response = client.post(
            "/delete/1",
            data={"cert_id": 1, "type": "resource"}
        )
        # assert delete error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("message", "Resource deleted successfully") in flashes

    def test_content_delete_resource_and_all_sections(self, client: FlaskClient) -> None:
        """
        Assert a Resource object is successfully delete from the DB

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create a resource
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # create a section
        requests.post(
            url=f"{API_URL}/section",
            data=json.dumps(self.section_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # delete the resource
        response = client.post(
            "/delete/1",
            data={"cert_id": 1, "type": "resource"}
        )
        # get the associated sections
        sections = requests.get(url=f"{API_URL}/section", timeout=2)
        section_data = sections.json()
        # assert delete error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("message", "Resource deleted successfully") in flashes and \
            len(section_data) == 0

    def test_content_delete_section(self, client: FlaskClient) -> None:
        """
        Assert a Section object is successfully delete from the DB

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create a section
        requests.post(
            url=f"{API_URL}/section",
            data=json.dumps(self.section_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # delete the section
        response = client.post(
            "/delete/1",
            data={"cert_id": 1, "type": "section"}
        )
        # assert delete error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("message", "Section deleted successfully") in flashes
