"""
Core app views module
"""

from flask import Blueprint, render_template, Response

core_bp = Blueprint(
    "core",
    __name__,
    template_folder="templates"
)


@core_bp.route("/")
def index() -> Response:
    """
    Site root

    Returns:
        Response: json object
    """
    return render_template("core.html", title="Cert Tracker")
