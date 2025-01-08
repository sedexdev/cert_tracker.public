"""
Content operations test module
"""

# pylint: disable=duplicate-code, line-too-long, too-many-public-methods, consider-using-with, too-many-lines

import json
import os

from io import BytesIO
from pathlib import Path

import requests

from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}"
    )
)

LOGO_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/logos")


class TestContent:
    """
    Content creation and management testing class
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.cert_data = None
        cls.resource_data = None
        cls.resource_data_og = None
        cls.section_data = None
        cls.section_import = None

    def setup_method(self) -> None:
        """
        Setup methods before each test runs
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
        # resource using Open Graph
        self.resource_data_og = {
            "cert_id": 1,
            "resource_type": "documentation",
            "url": "http://127.0.0.1:5000",
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
        # JSON import form data
        self.section_import = {
            "cert_id": 1,
            "resource_id": 1,
            "text_area": "",
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
        # clean up test images if created
        test_badge = Path(os.path.join(
            LOGO_PATH, "tests_images_BADGE_test.png"))
        test_site_logo = Path(os.path.join(LOGO_PATH, "site_logo.jpg"))
        if test_badge.exists():
            os.remove(test_badge)
        if test_site_logo.exists():
            os.remove(test_site_logo)

    # ===== /create/cert =====

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
        # create mock file uploads for images
        head_img = open(f"{self.cert_data['head_img']}", 'rb')
        self.cert_data["head_img"] = FileStorage(head_img)
        # create a cert
        client.post("/create/cert", data=self.cert_data)
        head_img.close()
        # update the cert
        self.cert_data["name"] = "Updated test"
        badge_img = open(f"{self.cert_data['badge_img']}", 'rb')
        self.cert_data["head_img"] = FileStorage(badge_img)
        client.post("/update/cert/1", data=self.cert_data)
        badge_img.close()
        # get the cert data
        response = requests.get(f"{API_URL}/cert/1", timeout=2)
        data = response.json()
        # assert updates were saved
        assert \
            data["name"] == "Updated test" and \
            data["head_img"] == "tst101/tests_images_BADGE_test.png"

    def test_update_cert_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts that a 404 response is returned if Cert not found

        Args:
            client (FlaskClient): Flask app test client
        """
        # create mock file uploads for images
        head_img = open(f"{self.cert_data['head_img']}", 'rb')
        self.cert_data["head_img"] = FileStorage(head_img)
        badge_img = open(f"{self.cert_data['badge_img']}", 'rb')
        self.cert_data["badge_img"] = FileStorage(badge_img)
        # update a cert that doesn't exist
        self.cert_data["name"] = "Updated test"
        client.post("/update/cert/1", data=self.cert_data)
        # close file handlers
        head_img.close()
        badge_img.close()
        # test for error response
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "Cert not found") in flashes

    # ===== /create/resource =====

    def test_content_create_resource_creates_course(self, client: FlaskClient) -> None:
        """
        Assert a Course object is created and saved in the DB

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # create mock file uploads for images
        image = open(f"{self.resource_data['image']}", 'rb')
        self.resource_data["image"] = FileStorage(image)
        site_logo = open(f"{self.resource_data['site_logo']}", 'rb')
        self.resource_data["site_logo"] = FileStorage(site_logo)
        client.post("/create/resource", data=self.resource_data)
        # close file handlers
        image.close()
        site_logo.close()
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        assert data["title"] == "Test Course"

    def test_content_create_resource_creates_article(self, client: FlaskClient) -> None:
        """
        Assert a Resource object is created and saved in the DB

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # create mock file uploads for images
        image = open(f"{self.resource_data['image']}", 'rb')
        self.resource_data["image"] = FileStorage(image)
        site_logo = open(f"{self.resource_data['site_logo']}", 'rb')
        self.resource_data["site_logo"] = FileStorage(site_logo)
        self.resource_data["resource_type"] = "article"
        client.post("/create/resource", data=self.resource_data)
        # close file handlers
        image.close()
        site_logo.close()
        # test resource was created
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        assert data["resource_type"] == "article"

    def test_content_create_resource_sets_has_og_data(self, client: FlaskClient) -> None:
        """
        Assert the "has_og_data" property is set when creating resource

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # create mock file uploads for images
        image = open(f"{self.resource_data['image']}", 'rb')
        self.resource_data["image"] = FileStorage(image)
        site_logo = open(f"{self.resource_data['site_logo']}", 'rb')
        self.resource_data["site_logo"] = FileStorage(site_logo)
        self.resource_data["has_og_data"] = True
        client.post("/create/resource", data=self.resource_data)
        # close file handlers
        image.close()
        site_logo.close()
        # test resource was created
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        assert data["has_og_data"]

    def test_content_create_resource_course_fails_constraint_title(self, client: FlaskClient) -> None:
        """
        Assert creating a Course resource fails the unique constraint for
        title when creating resource on the same Cert

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # read file contents into memory
        with open(f"{self.resource_data['image']}", 'rb') as image_file:
            image_content = image_file.read()
        with open(f"{self.resource_data['site_logo']}", 'rb') as site_logo_file:
            site_logo_content = site_logo_file.read()
        # create mock file uploads for images
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # first request
        client.post("/create/resource", data=self.resource_data)
        # create new mock file uploads for images for the second request
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # second request
        response = client.post("/create/resource", data=self.resource_data)
        # test for error messages
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("error", "Title must be unique") in flashes

    def test_content_create_resource_course_fails_constraint_url(self, client: FlaskClient) -> None:
        """
        Assert creating a Course resource fails the unique constraint for
        URL when creating resource on the same Cert

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # read file contents into memory
        with open(f"{self.resource_data['image']}", 'rb') as image_file:
            image_content = image_file.read()
        with open(f"{self.resource_data['site_logo']}", 'rb') as site_logo_file:
            site_logo_content = site_logo_file.read()
        # create mock file uploads for images
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # first request
        client.post("/create/resource", data=self.resource_data)
        # create new mock file uploads for images for the second request
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # second request - update title to force check for URL
        self.resource_data["title"] = "Another test course"
        response = client.post("/create/resource", data=self.resource_data)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("error", "URL must be unique") in flashes

    def test_content_create_resource_article_fails_constraint(self, client: FlaskClient) -> None:
        """
        Assert creating a Resource (article) resource fails the unique constraint

        Args:
            app (Flask): Flask app instance
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # update resource type for both requests
        self.resource_data["resource_type"] = "article"
        # read file contents into memory
        with open(f"{self.resource_data['image']}", 'rb') as image_file:
            image_content = image_file.read()
        with open(f"{self.resource_data['site_logo']}", 'rb') as site_logo_file:
            site_logo_content = site_logo_file.read()
        # create mock file uploads for images
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # first request
        client.post("/create/resource", data=self.resource_data)
        # create new mock file uploads for images for the second request
        self.resource_data["image"] = FileStorage(
            BytesIO(image_content),
            filename="image.jpg"
        )
        self.resource_data["site_logo"] = FileStorage(
            BytesIO(site_logo_content),
            filename="site_logo.jpg"
        )
        # second request
        client.post("/create/resource", data=self.resource_data)
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "Title must be unique") in flashes

    def test_content_create_resource_pulls_og_data(self, client: FlaskClient) -> None:
        """
        Assert Open Protocol metadata data is returned when the
        ResourceForm is submitted with an Open Graph compliant
        URL only 

            "title": "Cert Tracker",
            "image": "static/images/og_site_img.png",
            "description": "Track your certification study path with ease",
            "site_logo": "test.svg",
            "site_name": "Cert Tracker",

        Args:
            client (FlaskClient): Flask app test client
        """
        response = client.post("/create/resource", data=self.resource_data_og)
        assert b"static/images/og_site_img.png" in response.data

    def test_content_create_resource_catches_httperror(self, client: FlaskClient) -> None:
        """
        Asserts a HTTPError is caught if a non Open Graph
        compliant URL is provided. 

        **This test will use udemy.com since I know they block 
        crawlers but this may break tests in future if they 
        change it

        Args:
            client (FlaskClient): Flask app test client
        """
        self.resource_data_og["url"] = "https://www.udemy.com/course/70533-azure"
        response = client.post("/create/resource", data=self.resource_data_og)
        assert response.status_code == 204

    def test_content_create_resource_catches_valueerror(self, client: FlaskClient) -> None:
        """
        Asserts a ValueError is caught if the URL provided is
        not a correct URL type 

        Args:
            client (FlaskClient): Flask app test client
        """
        self.resource_data_og["url"] = "this_is_not_a_valid_url_type"
        response = client.post("/create/resource", data=self.resource_data_og)
        assert response.status_code == 204

    def test_content_create_resource_catches_urlerror(self, client: FlaskClient) -> None:
        """
        Asserts a URLError is caught if the URL provided 
        cannot be correctly verified (in this test case I 
        am passing HTTPS which is not configured)

        Args:
            client (FlaskClient): Flask app test client
        """
        self.resource_data_og["url"] = "https://127.0.0.1:5000"
        response = client.post("/create/resource", data=self.resource_data_og)
        assert response.status_code == 204

    # ===== /import/resource =====

    def test_import_resource_flashes_error(self, client: FlaskClient) -> None:
        """
        Assert error message flashed if no resources are selected

        Args:
            client (FlaskClient): Flask app test client
        """
        client.post("/import/resource", data={"cert_id": 1})
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert ("error", "No resources selected for import") in flashes

    def test_import_resource_imports_correctly(self, client: FlaskClient) -> None:
        """
        Assert resources are added to chosen cert successfully

        Args:
            client (FlaskClient): Flask app test client
        """
        # create 2 certs
        requests.post(
            f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        self.cert_data["name"] = "Test2"
        self.cert_data["code"] = "tst-102"
        requests.post(
            f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # create a resource on cert 1
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # import it into cert 2
        client.post("/import/resource", data={"cert_id": 2, "1": "on"})
        # assert resource is on cert 2
        response = requests.get(f"{API_URL}/resource", timeout=2)
        data = response.json()
        assert \
            response.status_code == 200 and \
            len(data) == 2 and \
            [r["cert_id"] for r in data] == [1, 2]

    # ===== /update/resource/<int:resource_id> =====

    def test_update_resource(self, client: FlaskClient) -> None:
        """
        Asserts that a Resource object is updated in the DB

        Args:
            client (FlaskClient): Flask app test client
        """
        # create cert for testing against
        client.post("/create/cert", data=self.cert_data)
        # create a resource
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # update the resource
        self.resource_data["title"] = "Updated test"
        client.post("/update/resource/1", data=self.resource_data)
        # get the resource data
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        # assert updates were saved
        assert data["title"] == "Updated test"

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

    # ===== /update/resource/complete =====

    def test_content_update_resource_complete_true(self, client: FlaskClient) -> None:
        """
        Asserts the Resource 'complete' attribute is updated to True

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
        # update the resource
        self.resource_data["resource_id"] = 1
        self.resource_data["complete"] = True
        client.post("/update/resource/complete", data=self.resource_data)
        # assert resource updated
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        assert data["complete"]

    def test_content_update_resource_complete_not_updated(self, client: FlaskClient) -> None:
        """
        Asserts the Resource 'complete' attribute is not updated if type is not 'course'

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
        # update the resource
        self.resource_data["resource_id"] = 1
        self.resource_data["resource_type"] = "article"
        response = client.post(
            "/update/resource/complete",
            data=self.resource_data
        )
        # assert resource error message flashed
        with client.session_transaction() as session:
            flashes = session.get("_flashes")
        assert \
            response.status_code == 302 and \
            ("error", "Only course type resources can be marked complete") in flashes

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
