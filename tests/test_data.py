"""
Test module for the data Blueprint
"""

import json
import os

import requests

from src.data.views import get_cert_resources, get_importable_resources

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


class TestData:
    """
    Data test class for testing resource fetching,
    routing, and
    """

    @classmethod
    def setup_class(cls) -> None:
        """
        Setup class before all tests run
        """
        cls.cert = None
        cls.course_data = None
        cls.section_data = None
        cls.video_data = None
        cls.article_data = None
        cls.document_data = None

    def setup_method(self) -> None:
        """
        Setup class before all tests run
        """
        # dummy cert data
        self.cert = {"id": 1}
        # section data
        self.section_data = {
            "cert_id": 1,
            "resource_id": 1,
            "number": 1,
            "title": "Test section",
            "cards_made": None,
            "complete": None,
        }
        # resource data for each type
        self.course_data = {
            "cert_id": 1,
            "resource_type": "course",
            "url": "http://test.test/course",
            "title": "Test course",
            "image": "test/test.png",
            "description": "This is a test course",
            "site_logo": "test.svg",
            "site_name": "Test",
            "has_og_data": False,
            "complete": False,
        }
        self.video_data = {
            "cert_id": 1,
            "resource_type": "video",
            "url": "http://test.test/video",
            "title": "Test video",
            "image": "test/test.png",
            "description": "This is a test video",
            "site_logo": "test.svg",
            "site_name": "Test",
            "has_og_data": False,
            "complete": None,
        }
        self.article_data = {
            "cert_id": 1,
            "resource_type": "article",
            "url": "http://test.test/article",
            "title": "Test article",
            "image": "test/test.png",
            "description": "This is a test article",
            "site_logo": "test.svg",
            "site_name": "Test",
            "has_og_data": False,
            "complete": None,
        }
        self.document_data = {
            "cert_id": 1,
            "resource_type": "documentation",
            "url": "http://test.test/document",
            "title": "Test document",
            "image": "test/test.png",
            "description": "This is a test document",
            "site_logo": "test.svg",
            "site_name": "Test",
            "has_og_data": False,
            "complete": None,
        }

    # ===== get_cert_resources() =====

    def test_get_cert_resources_returns_sections(self) -> None:
        """
        Assert get_cert_resources() returns list of 'section'
        type Resource objects
        """
        requests.post(
            url=f"{API_URL}/section",
            data=json.dumps(self.section_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_cert_resources(self.cert, "section")
        assert \
            len(result) == 1 and \
            result[0]["title"] == "Test section"

    def test_get_cert_resources_returns_courses(self) -> None:
        """
        Assert get_cert_resources() returns list of 'course'
        type Resource objects
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.course_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_cert_resources(self.cert, "course")
        assert \
            len(result) == 1 and \
            result[0]["title"] == "Test course"

    def test_get_cert_resources_returns_videos(self) -> None:
        """
        Assert get_cert_resources() returns list of 'video'
        type Resource objects
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.video_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_cert_resources(self.cert, "video")
        assert \
            len(result) == 1 and \
            result[0]["title"] == "Test video"

    def test_get_cert_resources_returns_articles(self) -> None:
        """
        Assert get_cert_resources() returns list of 'article'
        type Resource objects
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.article_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_cert_resources(self.cert, "article")
        assert \
            len(result) == 1 and \
            result[0]["title"] == "Test article"

    def test_get_cert_resources_returns_documents(self) -> None:
        """
        Assert get_cert_resources() returns list of 'documentation'
        type Resource objects
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.document_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_cert_resources(self.cert, "documentation")
        assert \
            len(result) == 1 and \
            result[0]["title"] == "Test document"

    # ===== get_importable_resources() =====

    def test_get_importable_resources_returns_empty_list(self) -> None:
        """
        Assert that an empty list is returned if no resources exist
        """
        result = get_importable_resources(self.cert)
        assert len(result) == 0 and isinstance(result, list)

    def test_get_importable_resources_returns_empty_list_id(self) -> None:
        """
        Assert that an empty list is returned if only resources with a 
        matching cert id exist
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.document_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_importable_resources(self.cert)
        assert len(result) == 0 and isinstance(result, list)

    def test_get_importable_resources_returns_resources(self) -> None:
        """
        Assert that all resources with a non-matching cert id are returned
        """
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.document_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        # create another resource with a different cert ID
        self.video_data["cert_id"] = 2
        requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(self.video_data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        result = get_importable_resources(self.cert)
        assert \
            len(result) == 1 and \
            isinstance(result, list) and \
            result[0]["title"] == "Test video"
