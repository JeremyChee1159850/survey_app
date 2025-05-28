from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.competitor_dao import CompetitorDAO
from project693.utils.session_manager import SessionManager
import os, uuid, json


#app.config["UPLOAD_FOLDER"] = "project693/static/img/"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "img")
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "gif"}

competitor_dao = CompetitorDAO()

# Ensure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/siteadmin/list_plants", methods=["GET"])
def list_plants():
    keyword = request.args.get("search", "")
    plants = competitor_dao.search_plants(keyword)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LISTPLANTS.value
    )

    return render_template(
        "competition/plant_list.html", plants=plants
    )


@app.route("/siteadmin/add_plants", methods=["GET", "POST"])
def add_plant():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.ADDPLANT.value
    )

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        invasiveness = request.form.get("invasiveness")
        image = request.files.get("image")
        image_filename = "default.png"
        if image and allowed_file(image.filename):
            ext = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid.uuid4()}{ext}"
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image.save(image_path)
        competitor_dao.add_plant(name, description, image_filename, invasiveness)
        flash("New Plant added successfully!", "success")
        return redirect(url_for("list_plants"))
    return render_template("competition/add_plant.html")


@app.route("/siteadmin/edit_plant/<int:id>", methods=["GET", "POST"])
def edit_plant(id):
    competitor = competitor_dao.get_plant_by_id(id)

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]     
        file = request.files.get("image")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            #current_directory = os.path.dirname(os.path.abspath(__file__))
            #base_dir = os.path.dirname(current_directory)
            #file.save(os.path.join(base_dir, "static", "img", filename))
            image = filename
        else:
            image = competitor.image
            
        competitor_dao.edit_plant(id, name, description, image)
        flash("Plant edited successfully!", "success")
        return redirect(url_for("list_plants"))
    
    return render_template("competition/edit_plant.html", competitor=competitor)


@app.route("/siteadmin/delete_plants/<int:id>", methods=["POST"])
def delete_plant(id):
    competitor_dao.delete_plant(id)
    flash("Plant deleted successfully!", "success")
    return redirect(url_for("list_plants"))