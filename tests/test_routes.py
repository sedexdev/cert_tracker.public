"""
App routes test module
"""

import json
import os

import requests

from flask.testing import FlaskClient

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


class TestRoutes:
    """
    Tests correct responses from app routes
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
        self.cert_data = {
            "name": "Test",
            "code": "tst-101",
            "date": "01/01/2000",
            "head_img": "test/test.jpg",
            "badge_img": "test/BADGE_test.png",
            "exam_date": "",
            "tags": "test",
        }

    # ===== / =====

    def test_core_index_returns_correct_page(self, client: FlaskClient) -> None:
        """
        Asserts the correct page is returned by core.index

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert b"Cert Tracker" in response.data

    def test_core_index_returns_200(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by core.index

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert response.status_code == 200

    # ===== /certs =====

    def test_certs_certs_returns_correct_page(self, client: FlaskClient) -> None:
        """
        Asserts the correct page is returned by certs.certs

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/certs")
        assert b"Certifications" in response.data

    def test_certs_certs_returns_200(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by certs.certs

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/certs")
        assert response.status_code == 200

    # ===== /search =====

    def test_certs_search_returns_correct_page(self, client: FlaskClient) -> None:
        """
        Asserts the correct page is returned by certs.search

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/search")
        assert b"Search" in response.data

    def test_certs_search_returns_200(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by certs.search

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/search")
        assert response.status_code == 200

    def test_certs_search_returns_307(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by certs.search

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.post("/search", data={"search": "test"})
        assert response.status_code == 307

    def test_certs_search_displays_empty_search_message(self, client: FlaskClient) -> None:
        """
        Assert message is displayed to user if search box is empty on submit
        """
        response = client.post("/search", data={"search": ""})
        assert b"Please provide a term to search for" in response.data

    # ===== /results =====

    def test_certs_results_returns_search_page(self, client: FlaskClient) -> None:
        """
        Asserts the search page is returned by certs.results without POST data

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/results")
        assert b"Search" in response.data

    def test_certs_results_returns_200(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by certs.results

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/results")
        assert response.status_code == 200

    def test_certs_results_returns_results_page_with_params(self, client: FlaskClient) -> None:
        """
        Asserts the results page is returned by certs.results without POST data

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.post("/results?search=test")
        assert b"Results" in response.data

    def test_certs_results_returns_200_with_params(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by certs.results

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.post("/results?search=test")
        assert response.status_code == 200

    # ===== /create/cert =====

    def test_content_create_returns_search_page(self, client: FlaskClient) -> None:
        """
        Asserts the search page is returned by content.create without POST data

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/create/cert")
        assert b"Create new cert" in response.data

    def test_content_create_returns_200(self, client: FlaskClient) -> None:
        """
        Asserts the correct code is returned by content.create

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/create/cert")
        assert response.status_code == 200

    # ===== /create/resource =====

    def test_content_create_resource_returns_405(self, client: FlaskClient) -> None:
        """
        Asserts the /create/resource page returns 405 for GET

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/create/resource")
        assert response.status_code == 405

    # ===== /certs/data/<int:cert_id> =====

    def test_certs_data_returns_200_with_og_data(self, client: FlaskClient) -> None:
        """
        Assert 200 is returned when fetching a cert with 
        Open Graph protocol data

        Args:
            client (FlaskClient): client returned by fixture
        """
        # create cert to fetch endpoint for
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # get the route for this cert
        og_test = json.dumps([{"testing": True}])
        response = client.get(f"/certs/data/1?og_data={og_test}")
        assert \
            response.status_code == 200 and \
            b"Test" in response.data

    def test_certs_data_returns_200_without_og_data(self, client: FlaskClient) -> None:
        """
        Assert 200 is returned when fetching a cert without 
        Open Graph protocol data

        Args:
            client (FlaskClient): client returned by fixture
        """
        # create cert to fetch endpoint for
        requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(self.cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        # get the route for this cert
        response = client.get("/certs/data/1")
        assert \
            response.status_code == 200 and \
            b"Test" in response.data

    def test_certs_data_returns_404(self, client: FlaskClient) -> None:
        """
        Assert 404 is returned if the cert doesn't exist

        Args:
            client (FlaskClient): client returned by fixture
        """
        # try to fetch a cert that doesn't exist
        response = client.get("/certs/data/1")
        assert \
            response.status_code == 404 and \
            b"not found" in response.data
