from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.competitor_dao import CompetitorDAO
from project693.dao.competition_dao import CompetitionDao
from project693.utils.session_manager import SessionManager
import os, uuid, json


app.config["UPLOAD_FOLDER"] = "project693/static/img/"
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "gif"}

competitor_dao = CompetitorDAO()
competition_dao = CompetitionDao()

# Ensure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/theme/<int:theme_id>/admin/list_competitors", methods=["GET"])
def list_competitors(theme_id):
    keyword = request.args.get("search", "")
    competitors = competitor_dao.search_competitor(keyword)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.COMPETITOR_SETUP.value
    )

    return render_template(
        "competition/competitor_management.html", competitors=competitors
    )


@app.route("/theme/<int:theme_id>/admin/add_competitors", methods=["GET", "POST"])
def add_competitor(theme_id):
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        invasiveness = request.form.get("invasiveness")
        image = request.files.get("image")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        image_filename = "default.png"
        if image and allowed_file(image.filename):
            ext = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid.uuid4()}{ext}"
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image.save(image_path)
        if lat and lon:
            competitor_location = json.dumps({"lat": lat, "lon": lon})
        else:
            competitor_location = None
        competitor_dao.add_competitor(name, description, image_filename, competitor_location, invasiveness)
        flash("New Competitor added successfully!", "success")
        return redirect(url_for("list_competitors", theme_id=theme_id))
    return render_template("competition/add_competitor.html")


@app.route("/theme/<int:theme_id>/admin/edit_competitor/<int:id>", methods=["GET", "POST"])
def edit_competitor(theme_id, id):
    competitor = competitor_dao.get_competitor_by_id(id)
    if isinstance(competitor.location, str):
        competitor.location = json.loads(competitor.location)
    
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        updated_lat = request.form.get("lat")
        updated_lon = request.form.get("lon")
        
        if updated_lat and updated_lon:
            competitor.location = json.dumps({"lat": float(updated_lat), "lon": float(updated_lon)})
            
        file = request.files.get("image")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            current_directory = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_directory)
            file.save(os.path.join(base_dir, "static", "img", filename))
            image = filename
        else:
            image = competitor.image
            
        competitor_dao.edit_competitor(id, name, description, image, competitor.location)
        flash("Competitor edited successfully!", "success")
        return redirect(url_for("list_competitors", theme_id=theme_id, id=id))
    
    return render_template("competition/edit_competitor.html", competitor=competitor)


@app.route("/theme/<int:theme_id>/admin/delete_competitiors/<int:id>", methods=["POST"])
def delete_competitor(theme_id, id):
    competitor_dao.delete_competitor(id)
    flash("Competitor deleted successfully!", "success")
    return redirect(url_for("list_competitors", theme_id=theme_id))


@app.route("/theme/<int:theme_id>/admin/competitors_pickup", methods=["GET", "POST"])
def competitor_pick(theme_id):
    competition_name = request.args.get("competition_name")
    keyword = request.args.get("search", "")

    competition_id = competition_dao.get_competition_id_by_name(competition_name)
    if not competition_id:
        return redirect(
            url_for(
                "competitor_pick",
                theme_id=theme_id,
                competition_name=competition_name,
                error="Competition not found",
            )
        )

    competitors = competitor_dao.search_competitor(keyword)
    existing_competitor_ids = {
        comp["id"]
        for comp in competition_dao.get_competitors_by_competition(competition_id)
    }

    if request.method == "POST":
        selected_competitor_ids = request.form.getlist("selected_competitor_ids[]")
        selected_competitor_ids = [int(id) for id in selected_competitor_ids if id]

        for competitor_id in selected_competitor_ids:
            if competitor_id in existing_competitor_ids:
                competition_dao.delete_competitor_from_competition(
                    competition_id, competitor_id
                )
            else:
                competition_dao.add_competitor_to_competition(
                    competition_id, competitor_id
                )

        flash("Competitor list updated successfully!", "success")
        return redirect(
            url_for("competitor_pick", theme_id=theme_id, competition_name=competition_name)
        )

    competition_status = competition_dao.get_competition_staus(competition_id)

    return render_template(
        "competition/competitor_pick.html",
        competitors=competitors,
        competition_status=competition_status,
        competition_name=competition_name,
        existing_competitor_ids=existing_competitor_ids,
    )


@app.route("/survey/", methods=["GET", "POST"])
def survey():
    if request.method == "GET":
        return render_template("survey_intro.html")  # new template with garden + age form

    # POST method – user submitted intro form
    session["session_id"] = str(uuid.uuid4())  # new session
    session["question_number"] = 1
    session["answers"] = []

    # Save form metadata
    has_garden = request.form.get("has_garden") == "yes"
    age_range = request.form.get("age_range")

    # Save metadata with placeholder reasoning
    competitor_dao.save_metadata(
        session_id=session["session_id"],
        reasoning=None,
        has_garden=has_garden,
        age=age_range
    )

    # Start tracking pairs
    SessionManager.set("used_invasive", [])
    SessionManager.set("used_non_invasive", [])

    pair = competitor_dao.get_random_pair([], [])
    if not pair:
        flash("Not enough competitors in the database!", "warning")
        return redirect(url_for("list_competitors", theme_id=1))

    SessionManager.set("last_pair", [pair[0].id, pair[1].id])

    return render_template("survey.html", pair=pair, question_number=1)


@app.route("/survey/next/", methods=["GET"])
def survey_next_get():
    qn = session.get("question_number", 1)

    if qn == 10:
        return render_template("survey_questionnaire.html")

    used_invasive = SessionManager.get("used_invasive") or []
    used_non_invasive = SessionManager.get("used_non_invasive") or []

    pair = competitor_dao.get_random_pair(
        used_invasive_ids=used_invasive,
        used_non_invasive_ids=used_non_invasive
    )

    if not pair:
        flash("Not enough competitors left to continue the survey.", "warning")
        return redirect(url_for("list_competitors", theme_id=1))

    SessionManager.set("last_pair", [pair[0].id, pair[1].id])

    return render_template("survey.html", pair=pair, question_number=qn)

@app.route("/survey/next/", methods=["POST"])
def survey_next():
    selected_id = request.form.get("selected_id")
    session_id = session.get("session_id")
    #user_id = SessionManager.get("user_id")  # None if anonymous

    # Current question number
    qn = session.get("question_number", 1)

    # Save answer immediately
    competitor_dao.survey_answer(
        session_id=session_id,
        question_number=qn,
        selected_competitor_id=selected_id
    )

    # Update answers list
    answers = SessionManager.get("answers") or []
    answers.append(selected_id)
    SessionManager.set("answers", answers)

    # Update used competitors list
    used_invasive = SessionManager.get("used_invasive") or []
    used_non_invasive = SessionManager.get("used_non_invasive") or []
    last_pair = SessionManager.get("last_pair") or []

    for comp_id in last_pair:
        competitor = competitor_dao.get_competitor_by_id(int(comp_id))
        if competitor.invasiveness == 'invasive':
            if competitor.id not in used_invasive:
                used_invasive.append(competitor.id)
        else:
            if competitor.id not in used_non_invasive:
                used_non_invasive.append(competitor.id)

    SessionManager.set("used_invasive", used_invasive)
    SessionManager.set("used_non_invasive", used_non_invasive)

    # Increment question number
    session["question_number"] = qn + 1

    # Redirect to GET route to show next question
    return redirect(url_for("survey_next_get"))


@app.route("/survey/questionnaire", methods=["POST"])
def survey_questionnaire():
    reasoning = request.form.get("reasoning")
    session_id = session.get("session_id")
    #user_id = SessionManager.get("user_id")

    # Save reasoning as question 10
    competitor_dao = CompetitorDAO()
    competitor_dao.update_reasoning(
    session_id=session_id,
    reasoning=reasoning
    )

    # Get all selected answers from session
    answers = SessionManager.get("answers") or []

    # Count invasive vs non-invasive
    invasive_count = 0
    non_invasive_count = 0

    for plant_id in answers:
        plant = competitor_dao.get_competitor_by_id(int(plant_id))
        if plant.invasiveness == 'invasive':
            invasive_count += 1
        else:
            non_invasive_count += 1

    total = invasive_count + non_invasive_count
    invasive_percent = round((invasive_count / total) * 100, 1) if total else 0
    non_invasive_percent = round((non_invasive_count / total) * 100, 1) if total else 0

     # Decide message
    if non_invasive_count >= 5:
        message = "🌿 Well done! You have a preference for native species. You're helping conserve New Zealand biodiversity."
    elif invasive_count >= 5:
        message = "⚠️ Be careful! You’re choosing non-native species and these can chomp the garden fence."
    else:
        message = "Thanks for your input! Your preferences have been recorded."

    # Log for dev
    print("Reasoning:", reasoning)
    print("Answers:", SessionManager.get("answers"))

    # Clear session
    SessionManager.remove("question_number")
    SessionManager.remove("answers")
    SessionManager.remove("reasoning")
    SessionManager.remove("used_invasive")
    SessionManager.remove("used_non_invasive")

    return render_template(
        "survey_complete.html",
        invasive_percent=invasive_percent,
        non_invasive_percent=non_invasive_percent,
        message=message
    )