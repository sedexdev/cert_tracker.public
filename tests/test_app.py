"""
Test module for the Flask app
"""

from flask.testing import FlaskClient


class TestApp:
    """
    Flask app test class
    """

    # ===== Test Secure HTTP Headers =====

    def test_response_includes_content_security_policy(self, client: FlaskClient) -> None:
        """
        Assert response includes Content-Security-Policy header

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert "Content-Security-Policy" in response.headers

    def test_response_includes_x_xss_protection(self, client: FlaskClient) -> None:
        """
        Assert response includes X-XSS-Protection header

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert "X-XSS-Protection" in response.headers

    def test_response_includes_strict_transport_security(self, client: FlaskClient) -> None:
        """
        Assert response includes Strict-Transport-Security header

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert "Strict-Transport-Security" in response.headers

    def test_response_includes_x_content_type_options(self, client: FlaskClient) -> None:
        """
        Assert response includes X-Content-Type-Options header

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert "X-Content-Type-Options" in response.headers

    def test_response_includes_x_frame_options(self, client: FlaskClient) -> None:
        """
        Assert response includes X-Frame-Options header

        Args:
            client (FlaskClient): client returned by fixture
        """
        response = client.get("/")
        assert "X-Frame-Options" in response.headers
