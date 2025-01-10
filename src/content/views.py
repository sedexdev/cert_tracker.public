"""
View module for new cert creation
"""

import datetime
import json
import os

import requests

from flask import Blueprint, flash, redirect, render_template, request, Response, url_for

from src.content.forms import CertForm, ResourceForm, SectionForm, SectionImportForm

from src.models.cert import Cert
from src.models.resource import Resource
from src.models.section import Section

from src.util.file import create_exam_reminder, delete_exam_reminder
from src.util.image import handle_image_upload, DEFAULT_BADGE, DEFAULT_HEAD, PROJECT_ROOT
from src.util.open_graph import handle_og_data

content_bp = Blueprint(
    "content",
    __name__,
    template_folder="templates"
)

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"


###########################
##### CERT OPERATIONS #####
###########################


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
        # create cert data object
        cert_data = {
            "name": form.data["name"],
            "code": form.data["code"],
            "tags": form.data["tags"],
        }
        # handle image uploads
        cert_dir = form.data["code"].lower().replace("-", "")
        # save head image file if provided else use default
        if form.head_img.data:
            cert_data["head_img"] = handle_image_upload(
                form.head_img.data,
                cert_dir
            )
        else:
            cert_data["head_img"] = DEFAULT_HEAD
        # save badge image file if provided else use default
        if form.badge_img.data:
            cert_data["badge_img"] = handle_image_upload(
                form.badge_img.data,
                cert_dir
            )
        else:
            cert_data["badge_img"] = DEFAULT_BADGE
        # create the cert
        response = requests.post(
            url=f"{API_URL}/cert",
            data=json.dumps(cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
            return redirect(url_for("certs.certs"), 302)
        flash("Create cert failed", "error")
        return render_template("new_cert.html", form=form, title="CT: Create")
    if form.head_img.errors or form.badge_img.errors:
        flash("Image uploads only (jpg, jpeg, png, svg)", "error")
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
    if form.validate_on_submit():
        # create cert data object
        cert_data = {
            "name": form.data["name"],
            "code": form.data["code"],
            "tags": form.data["tags"],
        }
        # handle image uploads
        cert_dir = form.data["code"].lower().replace("-", "")
        # save head image file if provided
        if form.head_img.data:
            cert_data["head_img"] = handle_image_upload(
                form.head_img.data,
                cert_dir
            )
        # save badge image file if provided
        if form.badge_img.data:
            cert_data["badge_img"] = handle_image_upload(
                form.badge_img.data,
                cert_dir
            )
        response = requests.put(
            url=f"{API_URL}/cert/{cert_id}",
            data=json.dumps(cert_data),
            headers={"Content-Type": "application/json"},
            timeout=2
        )
        data = response.json()
        if data["status"] == 200:
            flash(f"{data["message"]}", "message")
        else:
            flash(f"{data["message"]}", "error")
        return redirect(url_for("certs.certs"), 302)
    if form.head_img.errors or form.badge_img.errors:
        flash("Image uploads only (jpg, jpeg, png, svg)", "error")
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
    # catch empty date
    if not starting_from:
        flash("Please provide a valid date", "error")
        return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
    # get the cert data from the API
    response = requests.get(f"{API_URL}/cert/{cert_id}", timeout=2)
    data = response.json()
    # read correct data file
    if request.form.get("testing"):
        data_file = f"{PROJECT_ROOT}/tests/test_data.json"
    else:
        data_file = f"{PROJECT_ROOT}/email/data.json"
    # format values
    cert_code = data["code"].lower().replace("-", "")
    date_parts = data["exam_date"].split("/")
    date_parts.reverse()
    cert_exam_date = "-".join(date_parts)
    # check for delete op
    if request.form.get("delete"):
        deleted = delete_exam_reminder(data_file, cert_code)
        if not deleted:
            flash("Email reminder not set", "error")
            return redirect(url_for('data.cert_data', cert_id=cert_id), 302)
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
    # create cert object and update the appropriate file
    create_exam_reminder(data_file, cert_code, {
        "created": datetime.date.today().strftime("%d-%m-%Y"),
        "name": data["name"],
        "code": data["code"],
        "examDate": cert_exam_date,
        "frequency": request.form["frequency"],
        "starting_from": starting_from
    })
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


###############################
##### RESOURCE OPERATIONS #####
###############################


@content_bp.route("/create/resource", methods=["POST"])
def create_resource() -> None:
    """
    Creates a new resource on a Cert object
    """
    form = ResourceForm()
    cert_id = request.form["cert_id"]
    if form.validate_on_submit():
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
            "resource_type": form.resource_type.data,
            "url": form.url.data,
            "title": form.title.data,
            "description": form.description.data,
            "site_name": form.site_name.data,
        }
        # handle images by checking for Open Graph data or image upload
        response = requests.get(url=f"{API_URL}/cert/{cert_id}", timeout=2)
        data = response.json()
        cert_dir = data["code"].lower().replace("-", "")
        if form.image.data:
            cert_data["image"] = handle_image_upload(
                form.image.data,
                cert_dir
            )
        if form.site_logo.data:
            cert_data["site_logo"] = handle_image_upload(
                form.site_logo.data,
                cert_dir,
                logo=True
            )
        # check if OG image was provided
        if request.form.get("image"):
            cert_data["image"] = request.form["image"]
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
    if form.image.errors or form.site_logo.errors:
        flash("Image uploads only (jpg, jpeg, png, svg)", "error")
    return handle_og_data(cert_id, form.url.data)


@content_bp.route("/import/resource", methods=["POST"])
def import_resource() -> Response:
    """
    Imports selected resources into the chosen cert

    Returns:
        Response: Flask Response object
    """
    cert_id = request.form["cert_id"]
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
    cert_id = request.form["cert_id"]
    # get the existing data to update - API requires all attributes present
    response = requests.get(
        f"{API_URL}/resource/{resource_id}",
        timeout=2
    )
    db_data = response.json()
    if form.validate_on_submit():
        # fetch cert code for image uploads
        response = requests.get(url=f"{API_URL}/cert/{cert_id}", timeout=2)
        data = response.json()
        cert_dir = data["code"].lower().replace("-", "")
        # create the new data dictionary and update values
        resource_data = {
            "resource_type": form.resource_type.data,
            "url": form.url.data,
            "title": form.title.data,
            "description": form.description.data,
            "site_name": form.site_name.data,
        }
        if form.image.data:
            resource_data["image"] = handle_image_upload(
                form.image.data,
                cert_dir
            )
        if form.site_logo.data:
            resource_data["site_logo"] = handle_image_upload(
                form.site_logo.data,
                cert_dir,
                logo=True
            )
        # merge the updated form data
        db_data.update(resource_data)
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
    return Response(status=204)


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


##############################
##### SECTION OPERATIONS #####
##############################


def has_import_errors(sections: list) -> bool:
    """
    Handles errors that may occur during the import
    of sections from a JSON file

    Args:
        sections (list): list of section objects

    Returns:
        bool: True if errors found, False otherwise
    """
    if not isinstance(sections, list):
        flash("List of 'sections' not found", "error")
        return True
    # check all list objects have the correct fields
    for section in sections:
        if len(section) != 2:
            flash("Invalid number of section fields found", "error")
            return True
        if "number" not in section or "title" not in section:
            flash("Incorrect section fields found", "error")
            return True
    return False


@content_bp.route("/create/section", methods=["POST"])
def create_section() -> None:
    """
    Creates a new section on a 'course' type
    Resource object
    """
    cert_id = request.form["cert_id"]
    import_form = SectionImportForm()
    # handle JSON import option first
    if import_form.validate_on_submit():
        try:
            data = json.loads(import_form.text_area.data)
            # check sections list exists
            sections = data.get("sections", None)
            # handle errors
            if has_import_errors(sections):
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
    if form.validate_on_submit():
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
    return Response(status=204)


@content_bp.route("/update/section", methods=["POST"])
def update_section() -> Response:
    """
    Updates a section
    """
    form = SectionForm()
    if form.validate_on_submit():
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
    return Response(status=204)


#############################
##### DELETE OPERATIONS #####
#############################


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
