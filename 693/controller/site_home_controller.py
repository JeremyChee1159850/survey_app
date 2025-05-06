from flask import Flask
from flask import render_template
from datetime import datetime
from prototype.utils.session_manager import SessionManager
from prototype.controller import app


@app.route("/home/", methods=["GET"])
def site_home():
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.SITEHOME.value)
    return render_template("site_home.html")
