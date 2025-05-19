from flask import render_template
from datetime import datetime
import platform
from flask import session
from project693.controller import app
from project693.utils.session_manager import SessionManager


def format_date(date_obj):
    return date_obj.strftime("%d %b %Y").lstrip("0")


@app.route("/home/", methods=["GET"])
def site_home():
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.SITEHOME.value)
    return render_template("site_home.html")