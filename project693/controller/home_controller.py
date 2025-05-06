from flask import render_template
from datetime import datetime
import platform
from flask import session

from project693.controller import app
from project693.dao.competition_dao import CompetitionDao
from project693.utils.session_manager import SessionManager
from project693.model.user import User
from project693.dao.theme_dao import ThemeDao


def format_date(date_obj):
    return date_obj.strftime("%d %b %Y").lstrip("0")


@app.route("/theme/<int:theme_id>/home/", methods=["GET"])
def home(theme_id):
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.HOME.value)

    user_id = session.get("user_id")

    competition_dao = CompetitionDao()
    theme_dao = ThemeDao()
    theme_info = theme_dao.get_theme_by_id(theme_id)
    ongoing_competitions = competition_dao.get_competitions_by_theme_and_status(
        theme_id, "ongoing"
    )
    ended_competitions = competition_dao.get_competitions_by_theme_and_status(
        theme_id, "ended"
    )
    published_competitions = competition_dao.get_competitions_by_theme_and_status(
        theme_id, "published"
    )
    ongoing_competition_name = None
    ongoing_voting_start_date = None
    ongoing_voting_end_date = None
    ongoing_voting_end_date_2 = None
    if ongoing_competitions:
        ongoing_competition = ongoing_competitions[0]
        ongoing_competition_name = ongoing_competition.name
        ongoing_voting_start_date = format_date(ongoing_competition.voting_start_date)
        ongoing_voting_end_date = format_date(ongoing_competition.voting_end_date)
        ongoing_voting_end_date_2 = ongoing_competition.voting_end_date
    return render_template(
        "home.html",
        theme_info=theme_info,
        ongoing_competitions=ongoing_competitions,
        ended_competitions=ended_competitions,
        published_competitions=published_competitions,
        ongoing_competition_name=ongoing_competition_name,
        ongoing_voting_start_date=ongoing_voting_start_date,
        ongoing_voting_end_date=ongoing_voting_end_date,
        ongoing_voting_end_date_2=ongoing_voting_end_date_2,
        user_id =user_id
    )


@app.route("/home/", methods=["GET"])
def site_home():
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.SITEHOME.value)
    themeDao = ThemeDao()
    themes = themeDao.theme_list()
    return render_template("site_home.html", themes=themes)
