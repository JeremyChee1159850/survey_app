from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import jsonify
from project693.controller import app
from project693.dao.competition_dao import CompetitionDao
from project693.dao.competitor_dao import CompetitorDAO
from project693.utils.session_manager import SessionManager
from flask import request
from datetime import datetime
from project693.dao.theme_dao import ThemeDao

# list of finalized competitions
@app.route("/theme/<int:theme_id>/competition_results/", methods=["GET"])
def competition_results(theme_id):
    competition_dao = CompetitionDao()
    results = competition_dao.get_finalized_competition_results_by_theme(theme_id)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.COMPETITION_RESULTS.value
    )
    return render_template(
        "competition/competition_results.html",
        competition_results=results,
        theme_id=theme_id,
    )

# finalized competitions results
@app.route(
    "/theme/<int:theme_id>/voter/competition_details/<int:competition_id>",
    methods=["GET"],
)
def competition_details(theme_id, competition_id):
    competition_dao = CompetitionDao()
    details = competition_dao.competition_details(competition_id)
    competition_name = competition_dao.competition_name(competition_id)
    return render_template(
        "competition/competition_details.html",
        competition_details=details,
        competition_name=competition_name,
        theme_id=theme_id, 
    )


@app.route("/theme/<int:theme_id>/admin/competition_setup/", methods=["GET", "POST"])
def competition_setup(theme_id):
    if request.method == "GET":
        SessionManager.set(
            SessionManager.ACTIVE_PAGE, SessionManager.Page.COMPETITION_SETUP.value
        )

        return render_template(
            "competition/competition_setup.html",
            message="initial_entry",
            status="all",
        )
    else:
        status = request.form.get("status")
        competition_dao = CompetitionDao()
        competition_list = competition_dao.search_competitions(status, theme_id)

        message = ""
        if len(competition_list) == 0:
            message = "no_data"

        return render_template(
            "competition/competition_setup.html",
            message=message,
            competition_list=competition_list,
            status=status,
        )


@app.route("/admin/competition_end/", methods=["GET"])
def competition_end():
    specific_date = None
    if request.args.get("specific_date"):
        date_str = request.args.get("specific_date")
        specific_date = datetime.strptime(date_str, "%d-%m-%Y")

    competitionDao = CompetitionDao()
    message = competitionDao.update_status_for_expired_competitions(specific_date)

    return message


@app.route("/theme/<int:theme_id>/admin/competition_add", methods=["GET", "POST"])
def competition_add(theme_id):
    if request.method == "GET":
        SessionManager.set(
            SessionManager.ACTIVE_PAGE, SessionManager.Page.COMPETITION_SETUP.value
        )

        themeDao = ThemeDao()
        theme_name = themeDao.get_theme_by_id(theme_id).name
        return render_template(
            "competition/competition_add.html",
            current_date=datetime.now().date(),
            flag="add",
            theme_name=theme_name,
        )
    else:
        name = request.form.get("name")
        voting_start_date = request.form.get("voting_start_date")
        voting_end_date = request.form.get("voting_end_date")
        competition_dao = CompetitionDao()
        competition_dao.add_competition(
            name, voting_start_date, voting_end_date, theme_id
        )

        flash("Competition added successfully")
        return redirect(url_for("competition_setup", theme_id=theme_id))


@app.route("/theme/<int:theme_id>/admin/competition_delete", methods=["POST"])
def competition_delete(theme_id):
    id = request.form.get("id")
    competition_dao = CompetitionDao()
    competition_dao.del_competition(id)
    return jsonify({"status": "success"})


@app.route("/theme/<int:theme_id>/admin/competition_edit", methods=["GET", "POST"])
def competition_edit(theme_id):
    if request.method == "GET":
        id = request.args.get("id")
        competition_dao = CompetitionDao()
        competition = competition_dao.get_competition_by_id(id)
        SessionManager.set(
            SessionManager.ACTIVE_PAGE, SessionManager.Page.COMPETITION_SETUP.value
        )
        themeDao = ThemeDao()
        theme_name = themeDao.get_theme_by_id(theme_id).name
        return render_template(
            "competition/competition_add.html",
            current_date=datetime.now().date(),
            flag="edit",
            competition=competition,
            theme_name=theme_name,
        )
    else:
        id = request.form.get("id")
        name = request.form.get("name")
        voting_start_date = request.form.get("voting_start_date")
        voting_end_date = request.form.get("voting_end_date")

        competition_dao = CompetitionDao()
        competition_dao.edit_competition(id, name, voting_start_date, voting_end_date)

        flash("Competition edited successfully")
        return redirect(url_for("competition_setup", theme_id=theme_id))


@app.route("/theme/<int:theme_id>/admin/competition_launch", methods=["POST"])
def competition_launch(theme_id):
    id = request.form.get("id")
    competition_dao = CompetitionDao()
    flag, message = competition_dao.launch_competition(id, theme_id)
    if flag:
        return jsonify({"message": message, "status": "success"}), 200
    else:
        return jsonify({"message": message, "status": "error"}), 400
