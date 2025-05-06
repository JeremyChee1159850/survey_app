from flask import render_template, redirect, url_for, session, request, jsonify, flash
from project693.dao.theme_dao import ThemeDao
from project693.dao.user_dao import UserDao
from project693.controller import app
from project693.utils.session_manager import SessionManager
from datetime import datetime
import mysql.connector


@app.route("/theme/<int:theme_id>/voter/theme_list", methods=["GET"])
def theme_list(theme_id):

    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.MY_COMPETITION_APPLICATION.value
    )

    user_id = session.get("user_id")

    theme_dao = ThemeDao()
    user_dao = UserDao()
    user_info = user_dao.find_by_id(user_id)
    theme_list = theme_dao.theme_application_list(user_id)

    user_role = user_info.role.name

    return render_template(
        "theme/my_theme_list.html",
        theme_list=theme_list,
        user_role=user_role,
        user_id=user_id,
    )


@app.route("/voter/theme_create", methods=["POST"])
def theme_create():
    user_id = session.get("user_id")
    theme_dao = ThemeDao()
    user_dao = UserDao()

    user_info = user_dao.find_by_id(user_id)
    user_name = user_info.username
    user_role = user_info.role.name

    if request.method == "POST":
        theme_name = request.form.get("category")
        theme_description = request.form.get("description")
        existing_theme = theme_dao.theme_name_check(theme_name)

        if existing_theme:
            return (
                jsonify(
                    {
                        "message": "Competition name already exists. Please choose another name."
                    }
                ),
                400,
            )

        applying_time = datetime.now()
        status = "pending"

        theme_dao.theme_create(
            theme_name=theme_name,
            theme_description=theme_description,
            applicant=user_name,
            applicant_id=user_id,
            applying_time=applying_time,
            status=status,
            rejection_reason=None,
            operator_id=None,
            operator=None,
            operation_time=None,
        )

        return (
            jsonify({"message": "Competition created successfully!"}),
            200,
        )  # Return JSON success message


@app.route("/siteadmin/theme_review", methods=["GET"])
def theme_review():
    user_id = session.get("user_id")

    theme_dao = ThemeDao()
    user_dao = UserDao()
    user_info = user_dao.find_by_id(user_id)
    theme_list = theme_dao.theme_application_list(user_id)

    user_role = user_info.role.name

    SessionManager.set(
        SessionManager.ACTIVE_PAGE,
        SessionManager.Page.MANAGING_COMPETITION_APPLICATION.value,
    )
    return render_template(
        "theme/theme_review.html",
        theme_list=theme_list,
        user_role=user_role,
        user_id=user_id,
    )


@app.route("/voter/update_theme", methods=["POST"])
def update_theme():
    theme_dao = ThemeDao()
    data = request.get_json()

    theme_id = data["theme_id"]
    theme_name = data["theme_name"]
    theme_description = data["theme_description"]

    theme_dao.theme_update(theme_id, theme_name, theme_description)

    return jsonify({"success": True})


@app.route("/siteadmin/reject_theme", methods=["POST"])
def reject_theme():
    user_id = session.get("user_id")

    theme_dao = ThemeDao()
    user_dao = UserDao()
    user_info = user_dao.find_by_id(user_id)
    user_name = user_info.username

    data = request.get_json()
    operator_id = user_id
    operator = user_name
    status = "rejected"
    theme_id = data["theme_id"]
    rejection_reason = data.get("rejection_reason")
    operation_time = data.get("operation_time")

    theme_dao.reject_theme(
        theme_id, status, rejection_reason, operator_id, operator, operation_time
    )

    return jsonify({"success": True})


@app.route("/siteadmin/approve_theme", methods=["POST"])
def approve_theme():
    user_id = session.get("user_id")

    theme_dao = ThemeDao()
    user_dao = UserDao()
    user_info = user_dao.find_by_id(user_id)
    user_name = user_info.username

    data = request.get_json()
    operator_id = user_id
    operator = user_name
    status = "approved"
    donation_status = "disabled"
    donation_app_id = None
    theme_id = data["theme_id"]
    operation_time = data.get("operation_time")
    theme_name = data.get("theme_name")
    description = data.get("description")
    applicant = data.get("applicant")
    applicant_id = data.get("applicant_id")

    theme_dao.approve_theme(
        theme_id,
        status,
        operator_id,
        operator,
        operation_time,
        theme_name,
        description,
        applicant_id,
        donation_status,
        donation_app_id,
    )

    return jsonify({"success": True})
