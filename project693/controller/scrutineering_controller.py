from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import jsonify
from project693.controller import app
from project693.dao.competition_dao import CompetitionDao
from project693.dao.competitor_dao import CompetitorDAO
from project693.dao.scrutineering_dao import ScrutineeringDAO
from project693.dao.user_dao import UserDao
from project693.utils.session_manager import SessionManager
from project693.model.competition import Competition
from flask import request
from datetime import datetime


@app.route("/theme/<int:theme_id>/scrutineer/daily_votes", methods=["GET"])
def daily_votes(theme_id):
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DAILY_VOTES.value
    )
    scrutineering_dao = ScrutineeringDAO()
    result = scrutineering_dao.summary_votes(theme_id)

    summary_votes = []
    competition = None
    if len(result) > 0:
        competition = Competition(
            None, result[0][0], result[0][1], result[0][2], "ongoing"
        )
        end_date = datetime.now().date()
        dates = scrutineering_dao.generate_date_range(
            competition.voting_start_date, end_date
        )
        for date in dates:
            item = [date, ""]
            for row in result:
                if row[3] == date:
                    item[1] = row[4]
                    break
            summary_votes.append(item)
        summary_votes.reverse()

    return render_template(
        "/scrutineering/daily_votes.html",
        competition=competition,
        summary_votes=summary_votes,
    )


@app.route("/theme/<int:theme_id>/scrutineer/unusual_votes", methods=["GET", "POST"])
def unusual_votes(theme_id):
    competitionDao = CompetitionDao()
    competition_list = competitionDao.ongoing_or_ended_competition(theme_id)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LIST_OF_VOTES.value
    )

    if request.method == "GET":
        return render_template(
            "/scrutineering/unusual_votes.html",
            message="initial_entry",
            competition_list=competition_list,
            flag="list",
        )
    else:
        competition_id = request.form.get("competition_id").strip()
        ip = request.form.get("ip").strip()
        scrutineering_dao = ScrutineeringDAO()
        votes = scrutineering_dao.unusual_votes(competition_id, ip, theme_id)
        message = ""
        if len(votes) == 0:
            message = "no_data"

        return render_template(
            "/scrutineering/unusual_votes.html",
            message=message,
            votes=votes,
            competition_list=competition_list,
            ip=ip,
            competition_id=competition_id,
            flag="list",
        )


@app.route("/theme/<int:theme_id>/scrutineer/invalidate", methods=["POST"])
def invalidate(theme_id):
    data = request.get_json()
    ids = data.get("ids")
    scrutineeringDao = ScrutineeringDAO()
    scrutineeringDao.invalidate(ids)
    return jsonify({"status": "success"})


@app.route("/deactivate", methods=["POST"])  # Jeremy
def deactivate():
    data = request.get_json()
    ids = data.get("ids")  # List of vote IDs to get user IDs
    scrutineeringDao = ScrutineeringDAO()

    # Deactivate users based on the invalidated votes
    scrutineeringDao.deactivate(ids)

    return jsonify({"status": "success"})


@app.route(
    "/theme/<int:theme_id>/scrutineer/approving_competition", methods=["GET", "POST"]
)
def approving_competition(theme_id):
    if request.method == "GET":
        SessionManager.set(
            SessionManager.ACTIVE_PAGE, SessionManager.Page.APPROVING_COMPETITION.value
        )
        competitionDao = CompetitionDao()
        competition_list = competitionDao.search_competitions("ended", theme_id)
        return render_template(
            "/scrutineering/approving_competition.html",
            competition_list=competition_list,
        )
    else:
        competition_id = request.form.get("competition_id")
        competitionDao = CompetitionDao()
        competitionDao.finalize_competition(competition_id)
        competition = competitionDao.get_competition_by_id(competition_id)
        flash(
            f"Competition '{competition.name}' has been approved and is now published."
        )
        return redirect(url_for("approving_competition", theme_id=theme_id))


@app.route(
    "/theme/<int:theme_id>/scrutineer/unusual_votes_by_ip", methods=["GET", "POST"]
)  # Jeremy
def unusual_votes_by_ip(theme_id):
    competitionDao = CompetitionDao()
    competition_list = competitionDao.ongoing_or_ended_competition(theme_id)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LIST_OF_VOTES.value
    )

    scrutineering_dao = ScrutineeringDAO()

    # Get parameters from the query string (GET request)
    competition_id = request.args.get("competition_id", "").strip()

    # Fetch all results grouped by IP if a competition_id is provided, or fetch all results if not
    votes_by_ip = scrutineering_dao.unusual_votes_by_ip(theme_id)
    message = "no_data" if len(votes_by_ip) == 0 else ""

    return render_template(
        "/scrutineering/unusual_votes.html",
        message=message,
        votes_by_ip=votes_by_ip,
        competition_list=competition_list,
        competition_id=competition_id,
        flag="group_by_ip",
    )


@app.route("/theme/<int:theme_id>/scrutineer/list_voters", methods=["GET", "POST"])
def list_voters(theme_id):
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LIST_OF_VOTERS.value
    )

    current_user_id = SessionManager.get(SessionManager.USER)["id"]

    if request.method == "GET":
        return render_template(
            "/scrutineering/list_voters.html",
            current_user_id=current_user_id,  # Pass current user ID to template
            message="initial_entry",
        )
    else:
        username = request.form.get("username", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()

        scrutineering_dao = ScrutineeringDAO()

        # Fetch the voters based on the search criteria and theme_id
        voters = scrutineering_dao.list_voters(
            username,
            first_name,
            last_name,
            theme_id,
            current_user_id,  # pass current_user_id
        )

        message = ""
        if len(voters) == 0:
            message = "no_data"

        return render_template(
            "/scrutineering/list_voters.html",
            message=message,
            voters=voters,
            username=username,
            first_name=first_name,
            last_name=last_name,
            theme_id=theme_id,
            current_user_id=current_user_id,  # Pass current_user_id to template
        )


@app.route("/theme/<int:theme_id>/scrutineer/voter_details", methods=["GET"])
def voter_details(theme_id):
    voter_id = request.args.get("voter_id")

    scrutineering_dao = ScrutineeringDAO()

    details = scrutineering_dao.voter_details(voter_id, theme_id)

    return render_template("/scrutineering/voter_details.html", details=details)


@app.route("/theme/<int:theme_id>/scrutineer/theme_ban", methods=["POST"])
def theme_ban(theme_id):
    data = request.get_json()
    voter_id = data.get("voter_id")
    appeal_id = data.get("appeal_id") or None

    if not voter_id:
        return jsonify({"status": "error", "message": "Voter ID is required"}), 400

    scrutineeringDao = ScrutineeringDAO()
    # Step 1: Ban the voter from the theme
    scrutineeringDao.theme_ban(voter_id, theme_id)
    # Step 2: Invalidate the votes from ongoing and ended competitions
    scrutineeringDao.invalidate_votes(voter_id)
    return jsonify(
        {
            "status": "success",
            "message": "Voter banned from this theme and votes are invalidated.",
        }
    )


@app.route("/theme/<int:theme_id>/scrutineer/profile_voter", methods=["GET"])
def profile_voter(theme_id):
    voter_id = request.args.get("voter_id")
    scrutineering_dao = ScrutineeringDAO()
    user = scrutineering_dao.profile_voter(voter_id)
    profile_data = {
        "username": user["username"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "description": user["description"],
        "location": user["location"],
    }
    return jsonify(profile_data)


@app.route("/theme/<int:theme_id>/scrutineer/view_appeals", methods=["GET"])  # Jeremy
def view_appeals(theme_id):
    selected_status = request.args.get("status", "pending")
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.BAN_APPEAL_REQUESTS.value
    )
    scrutineering_dao = ScrutineeringDAO()
    appeals = scrutineering_dao.view_appeals(theme_id, selected_status)
    message = ""
    if len(appeals) == 0:
        message = "no_data"
    return render_template(
        "/scrutineering/view_appeals.html",
        message=message,
        appeals=appeals,
        theme_id=theme_id,
        selected_status=selected_status,
    )


@app.route(
    "/theme/<int:theme_id>/scrutineer/appeal/revoke/<int:appeal_id>", methods=["POST"]
)  # Jeremy
def revoke_appeal(theme_id, appeal_id):
    scrutineering_dao = ScrutineeringDAO()
    # Step 1: Fetch the appeal details using the appeal_id
    appeal_details = scrutineering_dao.appeal_details(appeal_id)
    # Step 2: Validate the appeal exists and hasn't been processed
    if not appeal_details:
        return jsonify({"status": "error", "message": "Appeal not found."}), 404
    # Step 3: Fetch the voter (appealer) ID from the appeal details
    voter_id = appeal_details["appealer_id"]
    # Step 4: Revalidate the voter's votes (change status from 'invalid' to 'valid')
    scrutineering_dao.validate_votes(voter_id)
    # Step 5: Update the appeal status to 'revoked'
    scrutineering_dao.update_appeal_status(appeal_id, "revoked", session["user_id"])
    # Step 6: Remove the user from the banned_voters table to unban them
    scrutineering_dao.remove_banned_voter(voter_id, theme_id)
    # Step 7: Return success response
    return jsonify(
        {
            "status": "success",
            "message": "Appeal revoked, voter unbanned, and votes validated.",
        }
    )


@app.route(
    "/theme/<int:theme_id>/scrutineer/appeal/uphold/<int:appeal_id>", methods=["POST"]
)  # Jeremy
def uphold_appeal(theme_id, appeal_id):
    scrutineering_dao = ScrutineeringDAO()
    appeal_details = scrutineering_dao.appeal_details(appeal_id)
    if not appeal_details:
        return jsonify({"status": "error", "message": "Appeal not found."}), 404
    voter_id = appeal_details["appealer_id"]
    reason = request.form.get("upholding_reason", None)
    scrutineering_dao.update_appeal_status(
        appeal_id, "upheld", session["user_id"], reason
    )
    return jsonify(
        {"status": "success", "message": "Appeal upheld and voter remains banned."}
    )


@app.route("/siteadmin/voting_integrity", methods=["GET"])
def voting_integrity():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.VOTING_INTEGRITY.value
    )
    scrutineering_dao = ScrutineeringDAO()
    banned_users = scrutineering_dao.voting_integrity()
    return render_template(
        "scrutineering/voting_integrity.html", banned_users=banned_users
    )


@app.route("/siteadmin/site_wide_ban", methods=["POST"])
def site_wide_ban():
    data = request.get_json()
    voter_id = data.get("voter_id")
    scrutineeringDao = ScrutineeringDAO()
    # Call the new site-wide ban DAO method to ban the user site-wide
    scrutineeringDao.site_wide_ban(voter_id)
    return jsonify(
        {"status": "success", "message": "Voter banned from voting site-wide."}
    )


# Modal window for voting integrity
@app.route("/siteadmin/banned_themes/<int:user_id>", methods=["GET"])
def banned_themes(user_id):
    scrutineering_dao = ScrutineeringDAO()
    banned_themes = scrutineering_dao.banned_themes(user_id)
    return jsonify(banned_themes)


@app.route("/siteadmin/sitewide_appeals", methods=["GET"])  # Jeremy
def sitewide_appeals():
    selected_status = request.args.get("status", "pending")
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.SITEWIDE_APPEAL_REQUESTS.value
    )

    scrutineering_dao = ScrutineeringDAO()  # Assuming you're using the same DAO
    sitewide_appeals = scrutineering_dao.sitewide_appeals(
        selected_status
    )  # Use the new DAO method for sitewide appeals

    message = ""
    if len(sitewide_appeals) == 0:
        message = "no_data"

    return render_template(
        "/scrutineering/sitewide_appeals.html",  # Create a separate template for sitewide appeals if needed
        message=message,
        appeals=sitewide_appeals,  # Pass the sitewide appeals data to the template
        selected_status=selected_status,
    )


@app.route("/siteadmin/appeal/revoke/<int:appeal_id>", methods=["POST"])  # Jeremy
def revoke_sitewide_appeal(appeal_id):
    scrutineering_dao = ScrutineeringDAO()

    # Step 1: Fetch the appeal details using the appeal_id
    appeal_details = scrutineering_dao.appeal_details(appeal_id)

    # Step 2: Ensure the appeal exists and it is for a site-wide ban
    if not appeal_details or appeal_details["ban_scope"] != "sitewide":
        return (
            jsonify(
                {"status": "error", "message": "Site-wide appeal not found or invalid."}
            ),
            404,
        )

    # Step 3: Fetch the voter (appealer) ID from the appeal details
    voter_id = appeal_details["appealer_id"]

    # Step 4: Revalidate the voter's votes (change status from 'invalid' to 'valid') across the site
    scrutineering_dao.validate_votes(voter_id)

    # Step 5: Update the appeal status to 'revoked'
    scrutineering_dao.update_appeal_status(appeal_id, "revoked", session["user_id"])

    # Step 6: Remove the site-wide ban from the user
    scrutineering_dao.remove_sitewide_ban(voter_id)

    # Step 7: Return success response
    return jsonify(
        {
            "status": "success",
            "message": "Site-wide appeal revoked, voter unbanned, and votes validated.",
        }
    )


@app.route("/siteadmin/appeal/uphold/<int:appeal_id>", methods=["POST"])  # Jeremy
def uphold_sitewide_appeal(appeal_id):
    scrutineering_dao = ScrutineeringDAO()

    # Step 1: Fetch the appeal details using the appeal_id
    appeal_details = scrutineering_dao.appeal_details(appeal_id)

    # Step 2: Ensure the appeal exists and is for a site-wide ban
    if not appeal_details or appeal_details["ban_scope"] != "sitewide":
        return (
            jsonify(
                {"status": "error", "message": "Site-wide appeal not found or invalid."}
            ),
            404,
        )

    # Step 3: Get the reason for upholding (optional)
    reason = request.form.get("upholding_reason", None)

    # Step 4: Update the appeal status to 'upheld'
    scrutineering_dao.update_appeal_status(
        appeal_id, "upheld", session["user_id"], reason
    )

    # Step 5: Return success response
    return jsonify(
        {
            "status": "success",
            "message": "Site-wide appeal upheld and voter remains banned.",
        }
    )
