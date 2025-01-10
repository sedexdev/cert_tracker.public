"""
Resource operations test module
"""

# pylint: disable=duplicate-code

import json
import os

from io import BytesIO
from pathlib import Path

import requests

from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}"
    )
)

CERT_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/tst102")
LOGO_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/logos")


class TestResource:
    """
    Resource creation and management test class
    """
    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.cert_data = None
        cls.resource_data = None
        cls.resource_data_og = None

    def setup_method(self) -> None:
        """
        Setup methods before each test runs
        """
        # create new cert from form
        self.cert_data = {
            "name": "Test",
            "code": "tst-102",
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

    def teardown_method(self) -> None:
        """
        Teardown methods after each test runs
        """
        # clean up test images if created
        test_badge = Path(os.path.join(
            LOGO_PATH, "tests_images_BADGE_test.png"))
        test_site_logo = Path(os.path.join(LOGO_PATH, "site_logo.jpg"))
        if test_badge.exists():
            os.remove(test_badge)
        if test_site_logo.exists():
            os.remove(test_site_logo)
        # remove test cert image directory
        if CERT_PATH.exists():
            for file in CERT_PATH.iterdir():
                file.unlink()
            CERT_PATH.rmdir()

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
        client.post("/create/resource", data=self.resource_data)
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
        self.resource_data["resource_type"] = "article"
        client.post("/create/resource", data=self.resource_data)
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
        self.resource_data["has_og_data"] = True
        client.post("/create/resource", data=self.resource_data)
        # test resource was created
        response = requests.get(f"{API_URL}/resource/1", timeout=2)
        data = response.json()
        assert data["has_og_data"]

    def test_content_create_resource_fails_constraint_title(self, client: FlaskClient) -> None:
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
        self.cert_data["name"] = "Test cert"
        self.cert_data["code"] = "tst-104"
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
