"""
User created routes for new certs
"""

# pylint: disable=line-too-long, too-many-locals

import json
import os

import requests

from flask import abort, Blueprint, render_template, Response, request

from src.content.forms import EmailReminderForm, ResourceForm, SectionForm, SectionImportForm
from src.models.cert import Cert

data_bp = Blueprint(
    "data",
    __name__,
    template_folder="templates",
    url_prefix="/certs/data"
)

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


def get_cert_resources(cert: Cert, resource_type: str) -> dict:
    """
    Requests resources of type <resource_type> from the API

    Args:
        cert (Cert): cert to fetch resources for
        resource_type (str): type of resource to fetch 

    Returns:
        dict: JSON response
    """
    if resource_type == "section":
        response = requests.get(f"{API_URL}/section", timeout=2)
        return response.json()
    response = requests.get(f"{API_URL}/resource", timeout=2)
    data = response.json()
    return [r for r in data if r["cert_id"] == cert["id"] and r["resource_type"] == resource_type]


def get_importable_resources(cert: Cert) -> list:
    """
    Gets all resources from the API and returns those whose
    which match the following criteria:

    - do not have a matching cert ID to the cert passed in
    - do not exist on the cert already
    - are not duplicate resources from multiple certs 
        - only a single resource data set is returned

    Args:
        cert (Cert): cert ID to exclude from results

    Returns:
        list: list of available resources to import into a cert
    """
    # get all resources
    response = requests.get(f"{API_URL}/resource", timeout=2)
    data = response.json()
    # get this certs resources
    cert_r = [r for r in data if r["cert_id"] == cert["id"]]
    # exclude resources already on this cert
    not_cert_r = [r for r in data if r["cert_id"] != cert["id"]]
    # remove duplicates
    r_dict = {}
    for i, r in enumerate(not_cert_r):
        if r["title"] not in r_dict:
            r_dict[r["title"]] = i
    # filtered list of unique resources
    filtered = [not_cert_r[i] for i in r_dict.values()]
    # return remaining resources
    importable = []
    for fr in filtered:
        # check if resource is in cert_r
        exists = False
        for r in cert_r:
            if fr["title"] == r["title"]:
                exists = True
                break
        if not exists:
            importable.append(fr)
    return importable


def fetch_cert(cert: Cert, tags: list, forms: tuple, og_data=None) -> str:
    """
    Fetches the cert data and returns the template with
    the data fields updated

    Args:
        cert (Cert): Cert object
        tags (list): list of Cert tags
        forms (tuple): creation forms
        og_data (None | dict): data pulled from opengraph

    Returns:
        str: template string
    """
    if og_data:
        og_result = json.loads(og_data)
        og_data_sent = True
    else:
        og_result = None
        og_data_sent = None
    courses = get_cert_resources(cert, "course")
    sections = get_cert_resources(cert, "section")
    videos = get_cert_resources(cert, "video")
    articles = get_cert_resources(cert, "article")
    documents = get_cert_resources(cert, "documentation")
    importable_resources = get_importable_resources(cert)
    email_reminder_form, resource_form, section_form, section_import_form = forms
    return render_template(
        template_name_or_list="cert_data.html",
        email_reminder_form=email_reminder_form,
        resource_form=resource_form,
        section_form=section_form,
        section_import_form=section_import_form,
        cert=cert,
        tags=tags,
        course_data=courses,
        section_data=sections,
        video_data=videos,
        article_data=articles,
        document_data=documents,
        resources={
            # courses are excluded as duplicating the section data is not beneficial
            "videos": [r for r in importable_resources if r["resource_type"] == "video"],
            "articles": [r for r in importable_resources if r["resource_type"] == "article"],
            "documents": [r for r in importable_resources if r["resource_type"] == "documentation"],
        },
        title=f"CT: {cert["name"]}",
        og_data=og_result,
        has_og_data=og_data_sent,
    )


@data_bp.route("/<int:cert_id>", methods=["GET", "POST"])
def cert_data(cert_id: int) -> Response:
    """
    Returns the cert_data template with the data for the
    Cert identified by the given ID

    Args:
        cert_id (str): name of the certificate

    Returns:
        Response: app response object
    """
    resource_form = ResourceForm()
    section_form = SectionForm()
    section_import_form = SectionImportForm()
    email_reminder_form = EmailReminderForm()
    cert = requests.get(f"{API_URL}/cert/{cert_id}", timeout=2)
    data = cert.json()
    if not data:
        abort(404)
    og_data = request.args.get("og_data", None)
    cert_obj = Cert.query.filter_by(id=data["id"]).first()
    if og_data:
        return fetch_cert(
            cert=data,
            tags=cert_obj.tags,
            forms=(
                email_reminder_form,
                resource_form,
                section_form,
                section_import_form
            ),
            og_data=og_data
        )
    return fetch_cert(
        cert=data,
        tags=cert_obj.tags,
        forms=(
            email_reminder_form,
            resource_form,
            section_form,
            section_import_form
        ),
    )
