"""
View module for new cert creation
"""

# pylint: disable=inconsistent-return-statements

import datetime
import json
import os

from urllib.error import HTTPError, URLError

import opengraph_py3
import requests

from flask import Blueprint, flash, redirect, render_template, request, Response, url_for

from src.content.forms import CertForm, ResourceForm, SectionForm, SectionImportForm
from src.models.cert import Cert
from src.models.resource import Resource
from src.models.section import Section

content_bp = Blueprint(
    "content",
    __name__,
    template_folder="templates"
)

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}/{os.pardir}"
    )
)


def handle_og_data(cert_id: int, url: str) -> Response:
    """
    Uses the Open Graph protocol to attempt to 
    populate the resource data fields in the 
    ResourceForm

    Args:
        cert_id (int): Cert object ID
        url (str): URL to parse

    Returns:
        Response: Flask Response object
    """
    try:
        og_data = opengraph_py3.OpenGraph(url)
        # just return if OG search is empty
        og_list = list(og_data.items())
        base_og_data = "scrape" in og_list[0] and "_url" in og_list[1]
        if len(og_list) == 2 and base_og_data:
            return Response(status=204)
        # get OG data as dict to send back to template
        og_dict = {}
        for key, value in og_data.items():
            og_dict[key] = value
        return redirect(
            url_for(
                'data.cert_data',
                cert_id=cert_id,
                og_data=json.dumps([og_dict]),
                has_og_data=True),
            307
        )
    except HTTPError:
        return Response(status=204)
    except ValueError:
        return Response(status=204)
    except URLError:
        return Response(status=204)


@content_bp.route("/create/cert", methods=["GET", "POST"])
def create_cert() -> Response:
    """
    Returns the cert creation form template

    Returns:
        Response: Response object
    """
    form = CertForm()
    if request.method == "POST" and form.validate_on_submit():
        failed_constraint = Cert.exists(form.name.data, form.code.data)
        if failed_constraint:
            flash(f"{failed_constraint} must be unique", "error")
            return render_template(
                "new_cert.html",
                form=form,
                data=form.data,
                failed=failed_constraint,
                title="CT: Create"
            )
        response = requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(form.data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash("Create cert failed", "error")
        return redirect(url_for("certs.certs"), 302)
    return render_template("new_cert.html", form=form, title="CT: Create")


@content_bp.route("/update/cert/<int:cert_id>", methods=["POST"])
def update_cert(cert_id: int) -> Response:
    """
    Updates the provided fields of a Cert object

    Args:
        cert_id (int): Cert object ID

    Returns:
        Response: Flask Response object
    """
    form = CertForm()
    if request.method == "POST" and form.validate_on_submit():
        response = requests.put(
            url=f"{API_URL}/cert/{cert_id}",
            data=json.dumps(form.data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash(f"{data["message"]}", "error")
        return redirect(url_for("certs.certs"), 302)


@content_bp.route("/update/cert/exam_date", methods=["POST"])
def update_cert_exam_date() -> Response:
    """
    Updates the exam date on a cert

    Returns:
        Response: Flask Response object
    """
    cert_id = request.form["cert_id"]
    exam_date = request.form["exam-date"]
    # catch empty date
    if not exam_date:
        flash("Please provide a valid date", "error")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
    # set new date
    cert = requests.get(f"{API_URL}/cert/{cert_id}", timeout=2)
    data = cert.json()
    date_values = exam_date.split("-")
    date_values.reverse()
    data["exam_date"] = "/".join(date_values)
    response = requests.put(
        url=f"{API_URL}/cert/{cert_id}",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        timeout=2
    )
    data = response.json()
    if data["status"] == 200:
        flash(f"{data["message"]}", "message")
    else:
        flash("Failed to update cert", "error")
    return redirect(url_for('data.cert_data', cert_id=cert_id), 302)


@content_bp.route("/update/cert/exam_reminder", methods=["POST"])
def update_cert_exam_reminder() -> Response:
    """
    Updates the exam reminder email settings on 
    a cert

    Returns:
        Response: Flask Response object
    """
    cert_id = request.form["cert_id"]
    starting_from = request.form.get("starting_from")
    if request.method == "POST":
        # catch empty date
        if not starting_from:
            flash("Please provide a valid date", "error")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
        # get the cert data from the API
        response = requests.get(f"{API_URL}/cert/{cert_id}", timeout=2)
        data = response.json()
        # format values
        cert_code = data["code"].lower().replace("-", "")
        date_parts = data["exam_date"].split("/")
        date_parts.reverse()
        # read correct data file
        if request.form.get("testing"):
            data_file = f"{PROJECT_ROOT}/tests/test_data.json"
        else:
            data_file = f"{PROJECT_ROOT}/email/data.json"
        # check for delete op
        if request.form.get("delete"):
            with open(data_file, "r+", encoding="utf-8") as file:
                config = json.loads(file.read())
                # delete the entry
                try:
                    del config[cert_code]
                except KeyError:
                    flash("Email reminder not set", "error")
                    return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
                # clear existing content
                file.seek(0)
                file.truncate()
                # write the data back
                file.write(json.dumps(config))
            # update the reminder field
            data["reminder"] = False
            requests.put(
                f"{API_URL}/cert/{cert_id}",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=2,
            )
            flash("Email reminder deleted", "message")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
        cert_exam_date = "-".join(date_parts)
        # create cert object
        cert_obj = {
            "created": datetime.date.today().strftime("%d-%m-%Y"),
            "name": data["name"],
            "code": data["code"],
            "examDate": cert_exam_date,
            "frequency": request.form["frequency"],
            "starting_from": starting_from
        }
        # update the appropriate file
        with open(data_file, "r+", encoding="utf-8") as file:
            config = json.loads(file.read())
            # clear existing content
            file.seek(0)
            file.truncate()
            # update the data
            config[cert_code] = cert_obj
            # write the data back
            file.write(json.dumps(config))
        # update the reminder field
        data["reminder"] = True
        requests.put(
            f"{API_URL}/cert/{cert_id}",
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=2,
        )
        flash("Email reminder set", "message")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)


@content_bp.route("/create/resource", methods=["POST"])
def create_resource() -> None:
    """
    Creates a new resource on a Cert object
    """
    form = ResourceForm()
    cert_id = request.form["cert_id"]
    if request.method == "POST" and form.validate_on_submit():
        failed_constraint = Resource.exists(
            cert_id,
            form.title.data,
            form.url.data
        )
        if failed_constraint:
            flash(f"{failed_constraint} must be unique", "error")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
        has_og_data = request.form.get("has_og_data", None)
        # construct the data
        cert_data = {
            "cert_id": cert_id,
            "has_og_data": bool(has_og_data == "True"),
            "complete": False,
            **form.data
        }
        response = requests.post(
            url=f"{API_URL}/resource",
            data=json.dumps(cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash("Create resource failed", "error")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
    return handle_og_data(cert_id, form.url.data)


@content_bp.route("/import/resource", methods=["POST"])
def import_resource() -> Response:
    """
    Imports selected resources into the chosen cert

    Returns:
        Response: Flask Response object
    """
    cert_id = request.form["cert_id"]
    if request.method == "POST":
        # get the IDs of the selected resources
        resources = []
        for value in request.form:
            if value != "cert_id":
                resources.append(value)
        # flash error if no resources selected
        if not resources:
            flash("No resources selected for import", "error")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
        # get resources and create new entries with the new cert ID
        for resource_id in resources:
            response = requests.get(
                f"{API_URL}/resource/{resource_id}",
                timeout=2
            )
            data = response.json()
            data["cert_id"] = cert_id
            requests.post(
                f"{API_URL}/resource",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
                timeout=2
            )
        flash("Resources imported successfully", "message")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)


@content_bp.route("/update/resource/<int:resource_id>", methods=["POST"])
def update_resource(resource_id: int) -> Response:
    """
    Updates the provided fields of a Resource object

    Args:
        cert_id (int): Resource object ID

    Returns:
        Response: Flask Response object
    """
    form = ResourceForm()
    # get the existing data to update - API requires all attributes present
    response = requests.get(
        f"{API_URL}/resource/{resource_id}",
        timeout=2
    )
    db_data = response.json()
    # merge the updated form data
    db_data.update(form.data)
    if request.method == "POST" and form.validate_on_submit():
        response = requests.put(
            url=f"{API_URL}/resource/{resource_id}",
            data=json.dumps(db_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash(f"{data["message"]}", "error")
        return redirect(url_for("data.cert_data", cert_id=db_data["cert_id"]), 302)


@content_bp.route("/update/resource/complete", methods=["POST"])
def update_resource_complete() -> Response:
    """
    Updates the complete attribute for a Resource
    object when the type is 'course'

    Returns:
        Response: Flask Response object
    """
    cert_id = request.form["cert_id"]
    if request.form["resource_type"] != "course":
        flash("Only course type resources can be marked complete", "error")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
    resource_id = request.form["resource_id"]
    response = requests.get(url=f"{API_URL}/resource/{resource_id}", timeout=2)
    resource_data = response.json()
    resource_data["complete"] = bool(request.form["complete"] == 'True')
    response = requests.put(
        url=f"{API_URL}/resource/{resource_id}",
        data=json.dumps(resource_data),
        headers={"Content-Type": "application/json"},
        timeout=2,
    )
    data = response.json()
    if data["status"] == 200:
        flash(f"{data["message"]}", "message")
    else:
        flash("Failed to update cert", "error")
    return redirect(url_for('data.cert_data', cert_id=cert_id), 302)


@content_bp.route("/create/section", methods=["POST"])
def create_section() -> None:
    """
    Creates a new section on a 'course' type
    Resource object
    """
    cert_id = request.form["cert_id"]
    import_form = SectionImportForm()
    # handle JSON import option first
    if request.method == "POST" and import_form.validate_on_submit():
        try:
            data = json.loads(import_form.text_area.data)
            # check sections list exists
            sections = data.get("sections", None)
            if not isinstance(sections, list):
                flash("List of 'sections' not found", "error")
                return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
            # check all list objects have the correct fields
            for section in sections:
                if len(section) != 2:
                    flash("Invalid number of section fields found", "error")
                    return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
                if "number" not in section or "title" not in section:
                    flash("Incorrect section fields found", "error")
                    return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
            # if all tests pass create each section
            for section in sections:
                data = {
                    "cert_id": cert_id,
                    "resource_id": request.form["resource_id"],
                    "number": section["number"],
                    "title": section["title"]
                }
                requests.post(
                    url=f"{API_URL}/section",
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json"},
                    timeout=2
                )
            flash("JSON imported successfully", "message")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
        except json.JSONDecodeError:
            flash("JSON improperly formatted", "error")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
    # handle single section upload
    form = SectionForm()
    if request.method == "POST" and form.validate_on_submit():
        resource_data = {
            "cert_id": cert_id,
            "resource_id": request.form["resource_id"],
            **form.data
        }
        response = requests.post(
            url=f"{API_URL}/section",
            data=json.dumps(resource_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash("Crate section failed", "message")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)


@content_bp.route("/update/section", methods=["POST"])
def update_section() -> Response:
    """
    Updates a section
    """
    form = SectionForm()
    if request.method == "POST" and form.validate_on_submit():
        section_id = request.form["section-id"]
        section = requests.get(f"{API_URL}/section/{section_id}", timeout=2)
        section_data = section.json()
        section_data["number"] = form.number.data
        section_data["title"] = form.title.data
        section_data["cards_made"] = form.cards_made.data
        section_data["complete"] = form.complete.data
        requests.put(
            url=f"{API_URL}/section/{section_id}",
            data=json.dumps(section_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        updated = request.form.get("updated", None)
        if updated == "true":
            flash("Section updated successfully", "message")
            return redirect(url_for("data.cert_data", cert_id=section_data["cert_id"]), 302)
        return Response(status=204)


@ content_bp.route("/delete/<int:resource_id>", methods=["POST"])
def delete(resource_id: int) -> Response:
    """
    Deletes the resource identified by the
    given ID

    Args:
        id (int): resource ID

    Returns:
        Response: Flask Response object
    """
    if request.method == "POST":
        resource_type = request.form["type"]
        if resource_type == "cert":
            response = Cert.delete(resource_id)
        elif resource_type == "section":
            response = Section.delete(resource_id)
        else:
            response = Resource.delete(resource_id)
        flash(
            f"{response["message"]}",
            "message" if response["status"] == 200 else "error"
        )
        if resource_type == "cert":
            return redirect(url_for("certs.certs"), 302)
        return redirect(url_for('data.cert_data', cert_id=request.form["cert_id"]), 302)
