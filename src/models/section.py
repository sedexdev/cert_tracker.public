"""
Module creating the Section model
"""

# pylint: disable=too-many-instance-attributes

from dataclasses import dataclass
import os

import requests

from src.db import db

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


@dataclass
class Section(db.Model):
    """
    Model defining a course section
    """

    __tablename__ = "sections"

    id: int = db.Column(db.Integer, primary_key=True)
    cert_id: int = db.Column('cert_id', db.ForeignKey('certs.id'))
    resource_id: int = db.Column('resource_id', db.ForeignKey('resources.id'))
    number: int = db.Column(db.Integer, nullable=False)
    title: str = db.Column(db.String(255), nullable=False)
    cards_made: bool = db.Column(db.Boolean)
    complete: bool = db.Column(db.Boolean)
    created: str = db.Column(db.String(64))
    updated: str = db.Column(db.String(64))

    @classmethod
    def delete(cls, section_id: int) -> None:
        """
        Deletes the given section

        Args:
            section_id (int): Section ID
        """
        response = requests.delete(
            f"{API_URL}/section/{section_id}",
            timeout=2
        )
        return response.json()
