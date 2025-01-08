"""
Utils for handling image uploads
"""

import os
import shutil

from pathlib import Path

import requests

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

API_URL = f"http://127.0.0.1:5000/api/v{os.environ["API_VERSION"]}"

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        __file__,
        f"{os.pardir}/{os.pardir}/{os.pardir}"
    )
)

UPLOAD_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data")
LOGO_PATH = Path(f"{PROJECT_ROOT}/src/static/images/data/logos")
DEFAULT_HEAD = "default_cert/default_head.png"
DEFAULT_BADGE = "default_cert/default_badge.svg"


def handle_image_upload(img: FileStorage, cert_dir: str, logo=False) -> str:
    """
    Gets the full path of an upload using the UPLOAD_PATH
    and the <cert_dir> values. Creates the directory if
    the full path doesn't currently exist. Saves the file
    to the local file system and returns the file path

    Args:
        img (FileStorage): FlaskWTF FileField upload
        cert_dir (str): name of directory to save upload
        logo (bool): True if this image is stored under logos

    Returns:
        str: updated dict of cert data
    """
    filename = secure_filename(img.filename)
    if logo:
        # only save the logo if it doesn't already exist
        logo_path = Path(os.path.join(LOGO_PATH, filename))
        if not logo_path.exists():
            img.save(logo_path)
        return filename
    full_path = Path(os.path.join(f"{UPLOAD_PATH}", cert_dir))
    if not full_path.exists():
        full_path.mkdir()
    img.save(os.path.join(full_path, filename))
    return os.path.join(cert_dir, filename)


def remove_images(cert_id: int) -> None:
    """
    Deletes the image directory for the cert identified 
    by <cert_id>

    Args:
        cert_id (int): Cert object id
    """
    # get the cert code so the image directory can be deleted
    response = requests.get(f"{API_URL}/cert/{cert_id}", timeout=2)
    data = response.json()
    cert_dir = data["code"].lower().replace("-", "")
    full_path = Path(os.path.join(f"{UPLOAD_PATH}", cert_dir))
    shutil.rmtree(str(full_path), ignore_errors=True)
