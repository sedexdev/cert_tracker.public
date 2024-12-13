"""
App error handler test module
"""

from flask.testing import FlaskClient


class TestErrorHandlers:
    """
    Flask app error handlers test class
    """

    def test_bad_route_returns_404(self, client: FlaskClient) -> None:
        """
        Asserts 404 response code returned when route not found

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/this/does/not/exist")
        assert response.status_code == 404

    def test_bad_route_returns_404_page(self, client: FlaskClient) -> None:
        """
        Asserts 404 response page returned

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/this/does/not/exist")
        assert b"<h1>Error 404</h1>" in response.data

    def test_invalid_method_returns_405(self, client: FlaskClient) -> None:
        """
        Asserts 405 response code returned when method not allowed

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.post("/certs")
        assert response.status_code == 405

    def test_invalid_method_returns_405_page(self, client: FlaskClient) -> None:
        """
        Asserts 405 response page returned

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.post("/certs")
        assert b"<h1>Error 405</h1>" in response.data
