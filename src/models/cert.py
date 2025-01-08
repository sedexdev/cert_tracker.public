"""
Module creating the Cert model
"""

# pylint: disable=too-many-instance-attributes

import os

from dataclasses import dataclass

import requests

from src.db import db
from src.models.resource import Resource
from src.models.section import Section

from src.util.image import remove_images

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


@dataclass
class Cert(db.Model):
    """
    Model defining cert specific data
    """

    __tablename__ = "certs"

    # information data
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(255), nullable=False, unique=True)
    code: str = db.Column(db.String(255), nullable=False, unique=True)
    head_img: str = db.Column(db.String(255), nullable=False)
    badge_img: str = db.Column(db.String(255), nullable=False)
    exam_date: str = db.Column(db.String(64))
    complete: bool = db.Column(db.Boolean)
    reminder: bool = db.Column(db.Boolean)
    cost: float = db.Column(db.Float)
    tags: str = db.Column(db.Text())
    created: str = db.Column(db.String(64), nullable=False)

    @classmethod
    def exists(cls, name: str, code: str) -> str:
        """
        Checks to see if a Cert exists in the database
        that would cause this creation to raise an 
        integrity violation

        Args:
            name (str): form name value
            code (str): form code value

        Returns:
            str: first value causing an integrity violation
        """
        certs = Cert.query.all()
        for cert in certs:
            if cert.name == name:
                return "Name"
            if cert.code == code:
                return "Code"
        return None

    @classmethod
    def find(cls, query: str) -> list:
        """
        Runs a query against this model to find
        all entries that match the query string.

        Searched fields are:
        - path
        - name
        - code
        - tags

        Args:
            query (str): term to match against

        Returns:
            list: matching entries
        """
        certs = Cert.query.all()
        results = []
        for cert in certs:
            if query in cert.name:
                results.append(cert)
                continue
            if query in cert.code:
                results.append(cert)
                continue
            if query in cert.tags:
                results.append(cert)
                break
        return results

    @classmethod
    def delete(cls, cert_id: int) -> str:
        """
        Deletes the Cert with the given ID

        Args:
            cert_id (int): Cert ID
        """
        # remove cert images
        remove_images(cert_id)
        # delete sections
        sections = Section.query.filter_by(cert_id=cert_id).all()
        for section in sections:
            requests.delete(f"{API_URL}/section/{section.id}", timeout=2)
        # delete resources
        resources = Resource.query.filter_by(cert_id=cert_id).all()
        for resource in resources:
            requests.delete(f"{API_URL}/resource/{resource.id}", timeout=2)
        # delete the cert
        response = requests.delete(f"{API_URL}/cert/{cert_id}", timeout=2)
        return response.json()
