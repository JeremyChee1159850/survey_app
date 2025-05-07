from flask import request, render_template, redirect, url_for, flash, session
from project693.controller import app
from project693.dao.user_dao import UserDao
from project693.model import User
from project693.model.privacy_settings import UserPrivacySettings
from werkzeug.utils import secure_filename
from project693.utils.hash_utils import get_password_hash, check_password_hash
from project693.utils.session_manager import SessionManager
from flask import jsonify
import os
import json


# Configure the file upload folder
app.config["UPLOAD_FOLDER"] = "project693/static/img/"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/theme/<int:theme_id>/voter/profile/", methods=["GET", "POST"])
def profile(theme_id):
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.get_full_user_info(user_id)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.USER_PROFILE.value
    )
    return render_template("user/profile.html", user=user)


@app.route("/theme/<int:theme_id>/voter/update_profile/", methods=["GET", "POST"])
def update_profile(theme_id):
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)

    if request.method == "POST":
        # Handle profile image update
        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

                # Replace old image with new one
                user.avatar = filename
                user_dao.update_user(user)
                flash("Profile image updated successfully!")
                return redirect(url_for("update_profile"))
        updated_email = request.form.get("email")
        updated_first_name = request.form.get("first_name")
        updated_last_name = request.form.get("last_name")
        updated_description = request.form.get("description")

        # Get updated location coordinates and round them to 2 decimal place
        lat_value = request.form.get("lat")
        lon_value = request.form.get("lon")
        if lat_value and lon_value:
            try:
                updated_lat = round(float(lat_value), 2)
                updated_lon = round(float(lon_value), 2)
                user.location = json.dumps({"lat": updated_lat, "lon": updated_lon})
            except ValueError:
                flash("Invalid latitude or longitude values. Please enter valid numbers.")
        else:
            flash("Latitude and longitude values are required.")

        if updated_lat and updated_lon:
            user.location = json.dumps({"lat": updated_lat, "lon": updated_lon})

        if updated_email:
            existing_user = user_dao.find_by_email(updated_email)
            if existing_user and existing_user.id != user_id:
                flash("Email already exists. Please use a different email.")
            else:
                user.email = updated_email
                user.first_name = updated_first_name
                user.last_name = updated_last_name
                user.description = updated_description

                user_dao.update_user(user)
                flash("Profile updated successfully!")
        return redirect(url_for("update_profile", theme_id=theme_id))

    return render_template("user/update_profile.html", user=user)


@app.route("/voter/delete_profile_image/", methods=["POST"])
def delete_profile_image():
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)

    # Reset avatar to default
    user.avatar = "default.png"
    user_dao.update_user(user)
    flash("Profile image deleted successfully!")
    return redirect(url_for("profile"))


@app.route("/theme/<int:theme_id>/voter/change_password", methods=["GET", "POST"])
def change_password(theme_id):
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.CHANGE_PASSWORD.value
    )
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)
    current_password = ""
    new_password = ""
    confirm_password = ""

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # Check if the current password is correct
        if not check_password_hash(user.password_hash, current_password):
            flash("Current password is incorrect.")
        # Check if the new password is the same as the current password
        elif check_password_hash(user.password_hash, new_password):
            flash("New password cannot be the same as the current password.")
        # Check if the new password and confirmation match
        elif new_password != confirm_password:
            flash("New passwords do not match.")
        else:
            # Update the password in the database
            hashed_password = get_password_hash(new_password)
            user.password_hash = hashed_password
            user_dao.update_user(user)
            flash("Password changed successfully!")
            return redirect(url_for("change_password", theme_id=theme_id))

    return render_template(
        "user/change_password.html",
        current_password=current_password,
        new_password=new_password,
        confirm_password=confirm_password,
    )


# List of Banned Competitions
@app.route("/theme/<int:theme_id>/voter/banned_competitions", methods=["GET"])  # Jeremy
def banned_competitions(theme_id):

    user_info = SessionManager.get(SessionManager.USER)
    if not user_info:
        return redirect(url_for("login"))

    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.MY_BAN.value)
    user_dao = UserDao()
    banned_competitions = user_dao.banned_competitions(user_info["id"])
    return render_template(
        "user/banned_competitions.html",
        competitions=banned_competitions,
        username=user_info["username"],
    )


@app.route("/theme/<int:theme_id>/voter/appeal", methods=["POST"])  # Jeremy
def appeal(theme_id):
    id = request.form.get("id")
    ban_theme_id = request.form.get("ban_theme_id")
    user_id = session.get("user_id")
    appeal_reason = request.form.get("appealReason")

    user_dao = UserDao()
    user_info = SessionManager.get(SessionManager.USER)
    username = user_info["username"]

    # Handle both site-wide and theme-specific appeals
    if ban_theme_id:
        user_dao.appeal(
            id=id,
            theme_id=ban_theme_id,
            user_id=user_id,
            username=username,
            appeal_reason=appeal_reason,
        )
    else:
        user_dao.appeal_sitewide(
            user_id=user_id, username=username, appeal_reason=appeal_reason
        )
    return redirect(url_for("banned_competitions", theme_id=theme_id))


@app.route("/voter/ban_count", methods=["GET"])
def get_ban_count():
    user_info = SessionManager.get(SessionManager.USER)
    if not user_info:
        return jsonify({"error": "User not logged in"}), 401
    user_id = user_info["id"]
    user_dao = UserDao()
    count = user_dao.get_ban_count(user_id)
    return jsonify({"count": count})


@app.route("/theme/<int:theme_id>/voter/privacy_settings/", methods=["GET", "POST"])
def privacy_settings(theme_id):
    if request.method == "GET":
        user = User.from_dict(SessionManager.get(SessionManager.USER))
        userDao = UserDao()
        privacy_settings = userDao.get_privacy_settings_by_id(user.id)

        SessionManager.set(
            SessionManager.ACTIVE_PAGE, SessionManager.Page.PRIVACYSETTINGS.value
        )
        return render_template(
            "user/privacy_settings.html", privacy_settings=privacy_settings
        )
    else:
        user = User.from_dict(SessionManager.get(SessionManager.USER))
        show_email = request.form.get("show_email") == "on"
        show_first_name = request.form.get("show_first_name") == "on"
        show_last_name = request.form.get("show_last_name") == "on"
        show_location = request.form.get("show_location") == "on"
        show_description = request.form.get("show_description") == "on"
        show_avatar = request.form.get("show_avatar") == "on"
        show_recent_post = request.form.get("show_recent_post") == "on"
        show_recent_vote = request.form.get("show_recent_vote") == "on"
        show_recent_donation = request.form.get("show_recent_donation") == "on"
        show_in_user_list = request.form.get("show_in_user_list") == "on"

        privacy_settings = UserPrivacySettings(
            None,
            user.id,
            show_email,
            show_first_name,
            show_last_name,
            show_location,
            show_description,
            show_avatar,
            show_recent_post,
            show_recent_vote,
            show_recent_donation,
            show_in_user_list,
        )
        userDao = UserDao()
        userDao.update_privacy_setting(privacy_settings)
        flash("Privacy settings updated successfully!")
        return redirect(url_for("privacy_settings", theme_id=theme_id))
