from flask import Flask
from flask import render_template
from flask import g, request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash, abort
from project693.controller import app
from project693.dao.user_dao import UserDao
from project693.dao.theme_dao import ThemeDao
from project693.model import User
from datetime import datetime
from project693.utils.hash_utils import get_password_hash
from project693.model import enums
from project693.utils.session_manager import SessionManager
import re
import json

# visitor's access paths
exempt_routes_patterns = [
    r"^/home/.*$",
    r"^/login/.*$",
    r"^/logout/$",
    r"^/register/.*$",
    r"^/about_us/$",
    r"^/admin/competition_end/.*$",
    r"^/static/.*$",
    r"^/survey/$",
    r"^/survey/next/$",
    r"^/survey/questionnaire$",
    r"^/favicon.ico$",
    r"^/theme/\d+/home/$",  # match /theme/1/home/
    r"^/theme/\d+/current_voting/$",  # match /theme/1/current_voting/
    r"^/theme/\d+/competition_results/$",  # match /theme/1/competition_results/
    r"^/theme/\d+/message/$",
]


def is_exempt_route(path):
    return any(re.match(pattern, path) for pattern in exempt_routes_patterns)


# role and permission mapping
role_permissions = {
    "voter": [
        r"^/voter/.*$",
        r"^/theme/\d+/voter/.*$",
    ],
    "scrutineer": [
        r"^/theme/\d+/voter/.*$",
        r"^/theme/\d+/scrutineer/.*$",
    ],
    "admin": [
        r"^/theme/\d+/voter/.*$",
        r"^/theme/\d+/scrutineer/.*$",
        r"^/theme/\d+/moderator/.*$",
        r"^/theme/\d+/admin/.*$",
    ],
    "siteadmin": [
        r"^/voter/.*$",
        r"^/theme/\d+/voter/.*$",
        r"^/theme/\d+/scrutineer/.*$",
        r"^/theme/\d+/moderator/.*$",
        r"^/theme/\d+/admin/.*$",
        r"^/siteadmin/.*$",
    ],
}


def is_allowed(role, path):
    return any(re.match(pattern, path) for pattern in role_permissions.get(role.value))


@app.before_request
def before_request():
    # Store user data in g.user if login
    if SessionManager.USER in session:
        user_dao = UserDao()
        user_id = session.get("user_id")
        result = user_dao.get_user_details(user_id)

        if result.status == enums.Status.INACTIVE:
            session.pop(SessionManager.USER, None)
            session.pop("login_username", None)
            session.pop("login_password", None)
            session.pop("user_role", None)
            session.pop("env", None)
            return redirect(url_for("login"))

        SessionManager.set(SessionManager.USER, result.to_dict())
        g.user = User.from_dict(SessionManager.get(SessionManager.USER))

        themeDao = ThemeDao()
        themes = themeDao.theme_list()
        session["theme_list"] = [theme.to_dict() for theme in themes]
    else:
        g.user = None

    # Check if the URL includes 'competition_id'
    path_parts = request.path.split("/")
    if len(path_parts) > 2 and path_parts[1] == "theme":
        try:
            g.theme_id = int(path_parts[2])

            # Compatible with the global page to display on the specific competition homepage.
            if g.theme_id == 0:
                g.theme_role = None
                g.community_role = None
            else:
                theme_dao = ThemeDao()
                theme = theme_dao.get_theme_by_id(g.theme_id)
                g.theme_name = theme.name
                # if the session exists and the user is under a theme, fetch the user's theme role if he have one.
                if SessionManager.USER in session:
                    user = User.from_dict(SessionManager.get(SessionManager.USER))
                    g.theme_role = (
                        user.theme_role_mapping.get(g.theme_id)
                        if user.theme_role_mapping
                        else None
                    )
                    g.community_role = (
                        user.community_role_mapping.get(g.theme_id)
                        if user.community_role_mapping
                        else None
                    )
        except ValueError:
            g.theme_id = None

    if request.path == "/":
        return redirect(url_for("site_home"))

    # if the request path is not in exempt_route, check if the user has logged in
    if not is_exempt_route(request.path):
        if SessionManager.USER not in session:
            session["next_url"] = request.url
            return redirect(url_for("login"))
        else:
            # if the user is logged in, check if the user has access permission
            allow = False
            user = User.from_dict(SessionManager.get(SessionManager.USER))

            while True:
                # if site admin can access
                if is_allowed(user.role, request.path):
                    allow = True
                    break

                # Compatible with the global page to display on the specific competition homepage.
                if g.theme_id == 0:
                    break

                # if competition admin or scrutineer can access
                if (
                    hasattr(g, "theme_role")
                    and g.theme_role != None
                    and is_allowed(g.theme_role, request.path)
                ):
                    allow = True
                    break

                break

            if not allow:
                abort(403)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # if the user has already logged in, navigate to the home page
        if SessionManager.USER in session:
            return redirect(url_for("site_home"))

        session["previous_page"] = (
            request.referrer
            if request.referrer != url_for("login")
            and request.referrer != url_for("register")
            else None
        )
        login_username = session.get("login_username", "")
        login_password = session.get("login_password", "")
        SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.LOGIN.value)
        return render_template(
            "auth/login.html",
            login_username=login_username,
            login_password=login_password,
        )
    else:
        login_username = request.form.get("login_username")
        login_password = request.form.get("login_password")
        session["login_username"] = login_username
        session["login_password"] = login_password
        user_dao = UserDao()
        result, message = user_dao.authenticate_user(login_username, login_password)
        if result is None:
            flash(message)
            return redirect(url_for("login"))
        else:
            SessionManager.set(SessionManager.USER, result.to_dict())
            session["user_role"] = result.role.value
            session["user_id"] = result.id
            session["env"] = app.env

            previous_page = session.get("previous_page") or session.pop(
                "next_url", url_for("site_home")
            )
            return redirect(previous_page)  # BUG 从注册页面过来会跳转到注册页面


@app.route("/logout/", methods=["GET"])
def logout():
    session.pop(SessionManager.USER, None)
    session.pop("login_username", None)
    session.pop("login_password", None)
    session.pop("user_role", None)
    session.pop("env", None)
    return redirect(url_for("login"))


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        # if the user has already logged in, navigate to the home page
        if SessionManager.USER in session:
            return redirect(url_for("site_home"))

        return render_template(
            "auth/register.html",
            currentdate=datetime.now().date(),
        )
    else:
        reg_user_name = request.form.get("reg_user_name")
        email = request.form.get("email")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        reg_password = request.form.get("reg_password")
        descripti = request.form.get("description") or ""
        location = request.form.get("location")  # Location input (lat/lon in JSON)

        avatar = request.form.get("avatar")
        if not avatar:
            avatar = "default.png"
        latitude = None
        longitude = None
        if location:
            location_data = json.loads(location)
            latitude = round(float(location_data.get("lat")), 2)
            longitude = round(float(location_data.get("lon")), 2)
            user_location = json.dumps(
                {"lat": latitude, "lon": longitude}
            )  # Convert to JSON string
        else:
            user_location = None
        user_dao = UserDao()
        existing_user = user_dao.find_by_email(email)
        if existing_user:
            flash("Email already exists. Please use a different email.")
            return render_template(
                "auth/register.html",
                currentdate=datetime.now().date(),
                reg_user_name=reg_user_name,
                email=email,
                firstname=firstname,
                lastname=lastname,
                reg_password=reg_password,
                confirm_password=reg_password,
                descripti=descripti,
                location=location,
            )
        user = User(
            None,
            reg_user_name,
            get_password_hash(reg_password),
            email,
            firstname,
            lastname,
            user_location,
            descripti,
            avatar,
            enums.Role.VOTER,
            enums.Status.ACTIVE,
            enums.VotingPermission.ALLOWED,
            None,
            None,
        )
        flag, message = user_dao.register(user)
        if flag:
            flash(message)
            return redirect(url_for("login"))
        else:
            flash(message)
            return render_template(
                "auth/register.html",
                currentdate=datetime.now().date(),
                reg_user_name=reg_user_name,
                email=email,
                firstname=firstname,
                lastname=lastname,
                reg_password=reg_password,
                confirm_password=reg_password,
                descripti=descripti,
                location=location,
            )


@app.route("/about_us/")
def about_us():
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.ABOUTUS.value)
    return render_template("about_us.html")
