from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import jsonify
from project693.controller import app
from project693.model import User
from project693.dao.user_dao import UserDao
from project693.utils.session_manager import SessionManager
from flask import request
from datetime import datetime
from project693.model.enums import Role, Status


@app.route("/backend_user_management/", methods=["GET", "POST"])
def backend_user_management():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.MANAGING_USER.value
    )

    current_user = session.get("user_id")

    if request.method == "GET":
        return render_template(
            "/management/backend_user_management.html", message="initial_entry"
        )
    else:
        username = request.form.get("qry_user_name")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        user_dao = UserDao()
        user_list = user_dao.search_backend_user(
            username, first_name, last_name, exclude_user=current_user
        )
        message = ""
        if len(user_list) == 0:
            message = "no_data"

        return render_template(
            "/management/backend_user_management.html",
            message=message,
            user_list=user_list,
            qry_user_name=username,
            first_name=first_name,
            last_name=last_name,
        )


@app.route("/admin/profile", methods=["GET"])
def get_profile():
    user_id = request.args.get("data_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    profile_data = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "description": user.description,
        "location": user.location,
        "role": user.role.value,
        "status": user.status.value,
    }
    return jsonify(profile_data)


@app.route("/admin/update-role-status", methods=["POST"])
def update_role_status():
    data = request.json
    user_id = data["id"]
    field = data["field"]
    value = data["value"]
    user_dao = UserDao()

    if field == "role":
        user_dao.update_role(user_id, Role[value.upper()])
    else:
        user_dao.update_status(user_id, Status[value.upper()])

    return jsonify({"status": "success"})


@app.route("/admin/add-backend-user", methods=["POST"])
def add_backend_user():
    user_dao = UserDao()
    success, message = user_dao.backend_user_add()
    if success:
        return jsonify({"status": "success", "message": message})
    else:
        return jsonify({"status": "error", "message": message})


@app.route("/admin/update-profile", methods=["POST"])
def update_backend_user_profile():
    data = request.json

    user_id = data.get("id")
    username = data.get("username")
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    location = data.get("location")
    description = data.get("description")
    role = data.get("role")
    user_dao = UserDao()

    current_user = user_dao.find_by_id(user_id)

    if current_user.email != email:
        existing_user_by_email = user_dao.find_by_email(email)
        if existing_user_by_email and existing_user_by_email.id != user_id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Email already exists. Please use a different email.",
                }
            )

    if current_user.username != username:
        existing_user_by_username = user_dao.find_by_username(username)
        if existing_user_by_username and existing_user_by_username.id != user_id:
            return jsonify(
                {
                    "status": "error",
                    "message": "Username already exists. Please use a different username.",
                }
            )

    user_dao.update_backend_user(
        user_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        location=location,
        description=description,
        role=role,
    )

    return jsonify({"status": "success"})
