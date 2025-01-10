"""
API operations test module
"""

# pylint: disable=duplicate-code

import json
import os

import requests

from flask import Flask
from flask.testing import FlaskClient

from src.models.cert import Cert
from src.models.resource import Resource
from src.models.section import Section


class TestAPI:
    """
    API testing class
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.api_url = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"
        cls.cert_data_1 = None
        cls.cert_data_2 = None
        cls.resource_data_1 = None
        cls.resource_data_2 = None
        cls.resource_data_og = None
        cls.section_data_1 = None
        cls.section_data_2 = None

    def setup_method(self) -> None:
        """
        Setup class before all tests run
        """
        # create new cert from form
        self.cert_data_1 = {
            "name": "Test",
            "code": "tst-101",
            "date": "01/01/2000",
            "head_img": "test/test.jpg",
            "badge_img": "etest/BADGE_test.png",
            "exam_date": "",
            "reminder": False,
            "complete": False,
            "cost": None,
            "tags": "test",
        }
        self.cert_data_2 = {
            "name": "Test2",
            "code": "tst-102",
            "date": "01/01/2000",
            "head_img": "test2/test2.jpg",
            "badge_img": "etest/BADGE_test2.png",
            "exam_date": "",
            "reminder": False,
            "complete": False,
            "cost": None,
            "tags": "test2",
        }
        # create a new resource on the cert
        self.resource_data_1 = {
            "cert_id": 1,
            "resource_type": "course",
            "url": "http://test.test",
            "title": "Test course",
            "image": "test/test.png",
            "description": "This is a test course",
            "site_logo": "test.svg",
            "site_name": "Test",
            "complete": False,
            "has_og_data": False,
        }
        self.resource_data_2 = {
            "cert_id": 1,
            "resource_type": "article",
            "url": "http://test.test2",
            "title": "Test article",
            "image": "test2/test2.png",
            "description": "This is a test article",
            "site_logo": "test2.svg",
            "site_name": "Test 2",
            "complete": False,
            "has_og_data": False,
        }
        # resource using Open Graph
        self.resource_data_og = {
            "resource_type": "documentation",
            "url": "http://127.0.0.1:5000",
            "origin": "certs.certs",
        }
        # create a new section on a course
        self.section_data_1 = {
            "cert_id": 1,
            "resource_id": 1,
            "number": 1,
            "title": "Test section",
            "cards_made": False,
            "complete": False,
        }
        self.section_data_2 = {
            "cert_id": 1,
            "resource_id": 1,
            "number": 2,
            "title": "Test section 2",
            "cards_made": False,
            "complete": False,
        }

    # ========== Test Create ==========

    def test_post_cert(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert that a Cert objected is created and saved in the
        database successfully

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        response = client.post(
            f"{self.api_url}/cert",
            data=json.dumps(self.cert_data_1),
            headers={"Content-Type": "application/json"}
        )
        data = response.json
        with app.app_context():
            cert = Cert.query.filter_by(id=1).first()
        assert \
            data["message"] == "Cert created successfully" and \
            data["status"] == 200 and \
            cert.name == "Test"

    def test_post_resource(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert that a Resource objected is created and saved in the
        database successfully

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        response = client.post(
            f"{self.api_url}/resource",
            data=json.dumps(self.resource_data_1),
            headers={"Content-Type": "application/json"},
        )
        data = response.json
        with app.app_context():
            resource = Resource.query.filter_by(id=1).first()
        assert \
            data["message"] == "Resource created successfully" and \
            data["status"] == 200 and \
            resource.title == "Test course"

    def test_post_section(self, app: Flask, client: FlaskClient) -> None:
        """
        Assert that a Section objected is created and saved in the
        database successfully

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        response = client.post(
            f"{self.api_url}/section",
            data=json.dumps(self.section_data_1),
            headers={"Content-Type": "application/json"},
        )
        data = response.json
        with app.app_context():
            section = Section.query.filter_by(id=1).first()
        assert \
            data["message"] == "Section created successfully" and \
            data["status"] == 200 and \
            section.title == "Test section"

    # ========== Test Read ==========

    def test_get_cert_returns_all_certs(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns all Cert objects

        Args:
            client (FlaskClient): client returned by fixture 
        """
        # create 2 certs
        cert_data = [self.cert_data_1, self.cert_data_2]
        for _, cert in enumerate(cert_data):
            requests.post(
                url=f"{self.api_url}/cert",
                data=json.dumps(cert),
                headers={"Content-Type": "application/json"},
                timeout=2
            )
        # get the certs
        response = client.get("/api/v1/cert")
        assert len(response.json) == 2

    def test_get_resource_returns_all_resources(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns all Resource objects

        Args:
            client (FlaskClient): client returned by fixture
        """
        # create 2 resources
        resource_data = [self.resource_data_1, self.resource_data_2]
        for _, resource in enumerate(resource_data):
            requests.post(
                url=f"{self.api_url}/resource",
                data=json.dumps(resource),
                headers={"Content-Type": "application/json"},
                timeout=2
            )
        # get the resources
        response = client.get("/api/v1/resource")
        assert len(response.json) == 2

    def test_get_section_returns_all_sections(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns all Section objects

        Args:
            client (FlaskClient): client returned by fixture
        """
        # create 2 sections
        section_data = [self.section_data_1, self.section_data_2]
        for _, section in enumerate(section_data):
            requests.post(
                url=f"{self.api_url}/section",
                data=json.dumps(section),
                headers={"Content-Type": "application/json"},
                timeout=2
            )
        # get the sections
        response = client.get("/api/v1/section")
        assert len(response.json) == 2

    def test_get_cert_returns_cert_by_id(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns a Cert object

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/cert",
            data=json.dumps(self.cert_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # get the cert
        response = client.get("/api/v1/cert/1")
        assert response.json["name"] == "Test"

    def test_get_resource_returns_resource_by_id(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns a Resource object

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/resource",
            data=json.dumps(self.resource_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # get the resource
        response = client.get("/api/v1/resource/1")
        assert response.json["title"] == "Test course"

    def test_get_section_returns_section_by_id(self, client: FlaskClient) -> None:
        """
        Asserts that the API gets and returns a Section object

        Args:
            client (FlaskClient): client returned by fixture 
        """
        requests.post(
            url=f"{self.api_url}/section",
            data=json.dumps(self.section_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # get the section
        response = client.get("/api/v1/section/1")
        assert response.json["title"] == "Test section"

    # ========== Test Update ==========

    def test_put_cert_updates_correctly(self, client: FlaskClient) -> None:
        """
        Asserts that an existing Cert object in the DB is updated

        Args:
            client (FlaskClient): client returned by fixture 
        """
        requests.post(
            url=f"{self.api_url}/cert",
            data=json.dumps(self.cert_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        update_response = client.put(
            "/api/v1/cert/1",
            data=json.dumps(self.cert_data_2),
            headers={"Content-Type": "application/json"},
        )
        get_response = requests.get(url=f"{self.api_url}/cert/1", timeout=2)
        data = get_response.json()
        assert \
            update_response.json["message"] == "Cert updated successfully" and \
            update_response.json["status"] == 200 and \
            data["name"] == "Test2"

    def test_put_cert_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts 404 status is returned if the Cert object does not exist

        Args:
            client (FlaskClient): client returned by fixture 
        """
        update_response = client.put(
            "/api/v1/cert/1",
            data=json.dumps(self.cert_data_2),
            headers={"Content-Type": "application/json"},
        )
        assert \
            update_response.json["message"] == "Cert not found" and \
            update_response.json["status"] == 404

    def test_put_resource_updates_correctly(self, client: FlaskClient) -> None:
        """
        Asserts that an existing Resource object in the DB is updated

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/resource",
            data=json.dumps(self.resource_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        update_response = client.put(
            "/api/v1/resource/1",
            data=json.dumps(self.resource_data_2),
            headers={"Content-Type": "application/json"},
        )
        get_response = requests.get(
            url=f"{self.api_url}/resource/1",
            timeout=2
        )
        data = get_response.json()
        assert \
            update_response.json["message"] == "Resource updated successfully" and \
            update_response.json["status"] == 200 and \
            data["title"] == "Test article"

    def test_put_section_updates_correctly(self, client: FlaskClient) -> None:
        """
        Asserts that an existing Section object in the DB is updated

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/section",
            data=json.dumps(self.section_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        update_response = client.put(
            "/api/v1/section/1",
            data=json.dumps(self.section_data_2),
            headers={"Content-Type": "application/json"},
        )
        get_response = requests.get(
            url=f"{self.api_url}/section/1",
            timeout=2
        )
        data = get_response.json()
        assert \
            update_response.json["message"] == "Section updated successfully" and \
            update_response.json["status"] == 200 and \
            data["title"] == "Test section 2"

    # ========== Test Delete ==========

    def test_delete_cert_by_id(self, client: FlaskClient) -> None:
        """
        Asserts a Cert object is deleted from the DB

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/cert",
            data=json.dumps(self.cert_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response = client.delete("/api/v1/cert/1")
        assert \
            response.json["message"] == "Cert deleted successfully" and \
            response.json["status"] == 200

    def test_delete_resource_by_id(self, client: FlaskClient) -> None:
        """
        Asserts a Resource object is deleted from the DB

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/resource",
            data=json.dumps(self.resource_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response = client.delete("/api/v1/resource/1")
        assert \
            response.json["message"] == "Resource deleted successfully" and \
            response.json["status"] == 200

    def test_delete_section_by_id(self, client: FlaskClient) -> None:
        """
        Asserts a Section object is deleted from the DB

        Args:
            client (FlaskClient): client returned by fixture
        """
        requests.post(
            url=f"{self.api_url}/section",
            data=json.dumps(self.section_data_1),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        response = client.delete("/api/v1/section/1")
        assert \
            response.json["message"] == "Section deleted successfully" and \
            response.json["status"] == 200

    def test_delete_cert_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts a 404 status is returned if the Cert doesn't exist

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.delete("/api/v1/cert/1")
        assert \
            response.json["message"] == "Cert not found" and \
            response.json["status"] == 404

    def test_delete_resource_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts a 404 status is returned if the Resource doesn't exist

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.delete("/api/v1/resource/1")
        assert \
            response.json["message"] == "Resource not found" and \
            response.json["status"] == 404

    def test_delete_section_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts a 404 status is returned if the Section doesn't exist

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.delete("/api/v1/section/1")
        assert \
            response.json["message"] == "Section not found" and \
            response.json["status"] == 404
