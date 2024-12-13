"""
Module creating the Resource model
"""

# pylint: disable=too-many-instance-attributes

import os

from dataclasses import dataclass

import requests

from src.db import db
from src.models.section import Section

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


@dataclass
class Resource(db.Model):
    """
    Model defining a resource for a cert page
    """

    __tablename__ = "resources"

    id: int = db.Column(db.Integer, primary_key=True)
    cert_id: int = db.Column('cert_id', db.ForeignKey('certs.id'))
    resource_type: str = db.Column(db.String(64), nullable=False)
    url: str = db.Column(db.Text(), nullable=False)
    title: str = db.Column(db.String(255), nullable=False)
    image: str = db.Column(db.String(255), nullable=False)
    description: str = db.Column(db.Text(), nullable=False)
    site_logo: str = db.Column(db.String(255), nullable=False)
    site_name: str = db.Column(db.String(255), nullable=False)
    has_og_data: bool = db.Column(db.Boolean)
    complete: bool = db.Column(db.Boolean)  # applies to course type resources
    created: str = db.Column(db.String(64))
    updated: str = db.Column(db.String(64))

    @classmethod
    def exists(cls, cert_id: int, title: str, url: str) -> str:
        """
        Checks to see if a Resource exists in the database
        that would cause this creation to raise an 
        integrity violation

        Args:
            cert_id (int): Cert object ID
            name (str): form name value
            code (str): form code value

        Returns:
            str: first value causing an integrity violation
        """
        resources = Resource.query.filter_by(cert_id=cert_id).all()
        for resource in resources:
            if resource.title == title:
                return "Title"
            if resource.url == url:
                return "URL"
        return None

    @classmethod
    def delete(cls, resource_id: int) -> None:
        """
        Deletes the Resource with the given ID

        Args:
            resource_id (int): Resource ID
        """
        # check if resource is a course
        resource = Resource.query.filter_by(id=resource_id).first()
        if resource.resource_type == "course":
            # delete associated sections
            sections = Section.query.filter_by(resource_id=resource_id).all()
            for section in sections:
                requests.delete(f"{API_URL}/section/{section.id}", timeout=2)
        # delete Resource object
        response = requests.delete(
            f"{API_URL}/resource/{resource.id}",
            timeout=2
        )
        return response.json()
