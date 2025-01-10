"""
Section operations test module
"""

# pylint: disable=duplicate-code

import json
import os

import requests

from flask.testing import FlaskClient

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


class TestSection:
    """
    Section creation and management test class
    """
    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.section_data = None
        cls.section_import = None

    def setup_method(self) -> None:
        """
        Setup methods before each test runs
        """
        # create a new section on a course
        self.section_data = {
            "cert_id": 1,
            "resource_id": 1,
            "number": 1,
            "title": "Test section",
            "cards_made": None,
            "complete": None,
        }
        # JSON import form data
        self.section_import = {
            "cert_id": 1,
            "resource_id": 1,
            "text_area": "",
        }

    # ===== /create/section =====

    def test_content_create_section_creates_section(self, client: FlaskClient) -> None:
        """
        Assert a Section object is created and saved in the DB

        Args:
            client (FlaskClient): Flask app test client
        """
        client.post("/create/section", data=self.section_data)
        response = requests.get(f"{API_URL}/section/1", timeout=2)
        data = response.json()
        assert data["title"] == "Test section"

    def test_create_section_import_json_successful(self, client: FlaskClient) -> None:
        """
        Asserts that multiple sections are created successfully when
        importing as JSON

        Args:
            client (FlaskClient): Flask app test client
        """
        self.section_import["text_area"] = """
            {
                "sections": [
                    { "number": 1, "title": "Example title" },
                    { "number": 2, "title": "Add more as needed..." }
                ]
            }
        """
        client.post("/create/section", data=self.section_import)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("message", "JSON imported successfully") in flashes

    def test_create_section_import_json_fails_formatting(self, client: FlaskClient) -> None:
        """
        Asserts that the JSONDecodeError is caught and the
        correct message is flashed

        Note: the JSON is missing quotes 

        Args:
            client (FlaskClient): Flask app test client
        """
        self.section_import["text_area"] = """
            {
                sections: [
                    { number: 1, title: Example title },
                    { number: 2, title: Add more as needed... }
                ]
            }
        """
        client.post("/create/section", data=self.section_import)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "JSON improperly formatted") in flashes

    def test_create_section_import_json_fails_sections_value(self, client: FlaskClient) -> None:
        """
        Asserts that JSON import fails if the "sections" value
        in the JSON string does not serialize to a Python List
        instance

        Args:
            client (FlaskClient): Flask app test client
        """
        self.section_import["text_area"] = """
            {
                "sections": ""
            }
        """
        client.post("/create/section", data=self.section_import)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "List of 'sections' not found") in flashes

    def test_create_section_import_json_fails_section_length(self, client: FlaskClient) -> None:
        """
        Asserts that JSON import fails if a dict in the sections
        list has the wrong number of items

        Args:
            client (FlaskClient): Flask app test client
        """
        self.section_import["text_area"] = """
            {
                "sections": [
                    { "number": 1, "title": "Example title" },
                    { "number": 2, "title": "Add more as needed..." },
                    { "number": 3, "title": "Test", "extraField": "fails" }
                ]
            }
        """
        client.post("/create/section", data=self.section_import)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "Invalid number of section fields found") in flashes

    def test_create_section_import_json_fails_section_fields(self, client: FlaskClient) -> None:
        """
        Asserts that JSON import fails if a dict in the sections
        list is missing the 'number' or 'title' field

        Args:
            client (FlaskClient): Flask app test client
        """
        self.section_import["text_area"] = """
            {
                "sections": [
                    { "number": 1, "title": "Example title" },
                    { "number": 2, "wrong": "fails" }
                ]
            }
        """
        client.post("/create/section", data=self.section_import)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "Incorrect section fields found") in flashes

    # ===== /update/section =====

    def test_content_update_section_updates_section(self, client: FlaskClient) -> None:
        """
        Assert a Section object is updated and saved in the DB

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
        # get the section
        response = requests.get(f"{API_URL}/section/1", timeout=2)
        data = response.json()
        # update the data on the section
        data["section-id"] = 1
        data["cards_made"] = True
        client.post("/update/section", data=data)
        # get the updated section
        response = requests.get(f"{API_URL}/section/1", timeout=2)
        data = response.json()
        assert data["cards_made"] and not data["complete"]
