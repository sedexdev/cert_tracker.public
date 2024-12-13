"""
Module defining an API for all CRUD operations
"""

import os

from datetime import datetime

from flask import Blueprint, jsonify, Response, request

from src.db import db
from src.models.cert import Cert
from src.models.resource import Resource
from src.models.section import Section

api_bp = Blueprint(
    name="api",
    import_name=__name__,
    url_prefix=f"/api/v{os.getenv("API_VERSION")}"
)


# =============== Cert CRUD Ops ===============

@api_bp.route("/cert")
def get_all_certs() -> Response:
    """
    Gets all Certs from the database

    Returns:
        Response: Flask Response object
    """
    certs = Cert.query.all()
    return jsonify(certs)


@api_bp.route("/cert/<int:cert_id>")
def get_cert(cert_id: int) -> Response:
    """
    Gets a Cert from the database by ID

    Args:
        int (cert_id): id of resource

    Returns:
        Response: Flask Response object
    """
    cert = Cert.query.filter_by(id=cert_id).first()
    return jsonify(cert)


@api_bp.route("/cert", methods=["POST"])
def post_cert() -> Response:
    """
    Creates a Cert using the provided JSON
    data string

    Returns:
        Response: Flask Response object
    """
    data = request.get_json()
    cert = Cert(
        name=data["name"],
        code=data["code"],
        head_img=data["head_img"],
        badge_img=data["badge_img"],
        exam_date=data["exam_date"],
        reminder=False,
        tags=data["tags"],
        created=datetime.now().strftime("%d/%m/%Y"),
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify({
        "message": "Cert created successfully",
        "status": 200,
    })


@api_bp.route("/cert/<int:cert_id>", methods=["PUT"])
def put_cert(cert_id: int) -> Response:
    """
    Updates a Cert in the database using the
    provided cert ID

    Args:
        int (cert_id): id of cert

    Returns:
        Response: Flask Response object
    """
    cert = Cert.query.filter_by(id=cert_id).first()
    if not cert:
        return jsonify({
            "message": "Cert not found",
            "status": 404,
        })
    data = request.get_json()
    cert.name = data["name"]
    cert.code = data["code"]
    cert.head_img = data["head_img"]
    cert.badge_img = data["badge_img"]
    cert.exam_date = data["exam_date"]
    if data.get("reminder") is not None:
        cert.reminder = data["reminder"]
    cert.tags = data["tags"]
    db.session.add(cert)
    db.session.commit()
    return jsonify({
        "message": "Cert updated successfully",
        "status": 200,
    })


@api_bp.route("/cert/<int:cert_id>", methods=["DELETE"])
def delete_cert(cert_id: int) -> Response:
    """
    Deletes a Cert from the database by ID

    Args:
        int (cert_id): id of resource

    Returns:
        Response: Flask Response object
    """
    cert = Cert.query.filter_by(id=cert_id).first()
    if not cert:
        return jsonify({
            "message": "Cert not found",
            "status": 404,
        })
    Cert.query.filter_by(id=cert_id).delete()
    db.session.commit()
    return jsonify({
        "message": "Cert deleted successfully",
        "status": 200
    })


# =============== Resource CRUD Ops ===============

@api_bp.route("/resource")
def get_all_resources() -> Response:
    """
    Gets all Resources from the database

    Returns:
        Response: Flask Response object
    """
    resources = Resource.query.all()
    return jsonify(resources)


@api_bp.route("/resource/<int:resource_id>")
def get_resource(resource_id: int) -> Response:
    """
    Gets a Resource from the database by ID

    Args:
        int (resource_id): id of resource

    Returns:
        Response: Flask Response object
    """
    resource = Resource.query.filter_by(id=resource_id).first()
    return jsonify(resource)


@api_bp.route("/resource", methods=["POST"])
def post_resource() -> Response:
    """
    Creates a Resource

    Returns:
        Response: Flask Response object
    """
    data = request.get_json()
    # add default images if none provided
    image = data["image"] if data["image"] else "default_image.jpg"
    logo = data["site_logo"] if data["site_logo"] else "default_logo.png"
    resource = Resource(
        cert_id=data["cert_id"],
        resource_type=data["resource_type"],
        url=data["url"],
        title=data["title"],
        image=image,
        description=data["description"],
        site_logo=logo,
        site_name=data["site_name"],
        has_og_data=data["has_og_data"],
        complete=data["complete"],
        created=datetime.now().strftime("%m/%d/%Y:%H:%M:%S"),
    )
    db.session.add(resource)
    db.session.commit()
    return jsonify({
        "message": "Resource created successfully",
        "status": 200,
    })


@api_bp.route("/resource/<int:resource_id>", methods=["PUT"])
def put_resource(resource_id: int) -> Response:
    """
    Updates a Resource in the database

    Args:
        int (resource_id): id of resource

    Returns:
        Response: Flask Response object
    """
    data = request.get_json()
    resource = Resource.query.filter_by(id=resource_id).first()
    if not resource:
        return jsonify({
            "message": "Resource not found",
            "status": 404,
        })
    # add default images if none provided
    image = data["image"] if data["image"] else "default_image.jpg"
    logo = data["site_logo"] if data["site_logo"] else "default_logo.png"
    resource.resource_type = data["resource_type"]
    resource.url = data["url"]
    resource.title = data["title"]
    resource.image = image
    resource.description = data["description"]
    resource.site_logo = logo
    resource.site_name = data["site_name"]
    resource.complete = data["complete"]
    resource.updated = datetime.now().strftime("%m/%d/%Y:%H:%M:%S")
    db.session.commit()
    return jsonify({
        "message": "Resource updated successfully",
        "status": 200,
    })


@api_bp.route("/resource/<int:resource_id>", methods=["DELETE"])
def delete_resource(resource_id: int) -> Response:
    """
    Deletes a Resource from the database by ID

    Args:
        int (resource_id): id of resource

    Returns:
        Response: Flask Response object
    """
    deletions = Resource.query.filter_by(id=resource_id).delete()
    if deletions > 0:
        db.session.commit()
        return jsonify({
            "message": "Resource deleted successfully",
            "status": 200
        })
    return jsonify({
        "message": "Resource not found",
        "status": 404,
    })


# =============== Section CRUD Ops ===============

@api_bp.route("/section")
def get_all_sections() -> Response:
    """
    Gets all Sections from the database

    Returns:
        Response: Flask Response object
    """
    sections = Section.query.all()
    return jsonify(sections)


@api_bp.route("/section/<int:section_id>")
def get_section(section_id: int) -> Response:
    """
    Gets a Section from the database by ID

    Args:
        int (section_id): id of resource

    Returns:
        Response: Flask Response object
    """
    section = Section.query.filter_by(id=section_id).first()
    return jsonify(section)


@api_bp.route("/section", methods=["POST"])
def post_section() -> Response:
    """
    Creates a Section

    Returns:
        Response: Flask Response object
    """
    data = request.get_json()
    section = Section(
        cert_id=data["cert_id"],
        resource_id=data["resource_id"],
        number=data["number"],
        title=data["title"],
        created=datetime.now().strftime("%m/%d/%Y:%H:%M:%S"),
    )
    db.session.add(section)
    db.session.commit()
    return jsonify({
        "message": "Section created successfully",
        "status": 200,
    })


@api_bp.route("/section/<int:section_id>", methods=["PUT"])
def put_section(section_id: int) -> Response:
    """
    Updates a Section in the database

    Args:
        int (section_id): id of section

    Returns:
        Response: Flask Response object
    """
    data = request.get_json()
    section = Section.query.filter_by(id=section_id).first()
    if not section:
        return jsonify({
            "message": "Section not found",
            "status": 404,
        })
    section.number = data["number"]
    section.title = data["title"]
    section.cards_made = data["cards_made"]
    section.complete = data["complete"]
    section.updated = datetime.now().strftime("%m/%d/%Y:%H:%M:%S")
    db.session.commit()
    return jsonify({
        "message": "Section updated successfully",
        "status": 200,
    })


@api_bp.route("/section/<int:section_id>", methods=["DELETE"])
def delete_section(section_id: int) -> Response:
    """
    Deletes a Section from the database by ID

    Args:
        int (section_id): id of resource

    Returns:
        Response: Flask Response object
    """
    deletions = Section.query.filter_by(id=section_id).delete()
    if deletions > 0:
        db.session.commit()
        return jsonify({
            "message": "Section deleted successfully",
            "status": 200
        })
    return jsonify({
        "message": "Section not found",
        "status": 404,
    })
