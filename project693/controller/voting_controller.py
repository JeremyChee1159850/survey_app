from flask import render_template, session, redirect, url_for, flash, request
from project693.dao.competition_dao import CompetitionDao
from project693.dao.vote_dao import VoteDao
from project693.dao.user_dao import UserDao
from project693.controller import app
from project693.utils.session_manager import SessionManager

competition_dao = CompetitionDao()
vote_dao = VoteDao()
user_dao = UserDao()

# list of competitors under a theme
@app.route("/theme/<int:theme_id>/current_voting/", methods=["GET"])
def current_voting(theme_id):
    competitions = competition_dao.get_competitions_by_theme_and_status(theme_id, "ongoing")
    session.pop("competitor_id", None)
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.VOTING.value)
    voted_competitors = {}
    user_id = session.get("user_id")
    for competition in competitions:
        competition.formatted_start_date = competition.voting_start_date.strftime('%d %b %Y')
        competition.formatted_end_date = competition.voting_end_date.strftime('%d %b %Y')
        competitor_votes = competition_dao.get_competitor_votes(competition.id)
        for index, (competitor_id, competitor_name, vote_count) in enumerate(competitor_votes, start=1):
            competitor = next(c for c in competition.competitors if c.id == competitor_id)
            competitor.vote_count = vote_count
            competitor.vote_rank = index if index <= 3 else None  
        if user_id:
            voted_name = vote_dao.get_voted_competitor_name(competition.id, user_id)
            voted_competitors[competition.id] = voted_name
    recent_voters = {
        competition.id: vote_dao.get_recent_voters(competition.id)
        for competition in competitions
    }
    voter_locations = {
        competition.id: vote_dao.get_voter_locations(competition.id)
        for competition in competitions
    }
    return render_template(
        "competition/current_voting.html",
        competitions=competitions,
        recent_voters=recent_voters,
        voter_locations=voter_locations, 
        voted_competitors=voted_competitors,
        theme_id=theme_id
    )

# view competitor details
@app.route("/theme/<int:theme_id>/voter/competition/<int:competition_id>/competitor/<int:competitor_id>")
def competitor_details(theme_id, competition_id, competitor_id):
    session["competition_id"] = competition_id
    session["competitor_id"] = competitor_id
    user_id = session.get("user_id")
    competition_competitor, competitor = competition_dao.get_competitor_details(
        competitor_id
    )
    if not competition_competitor:
        session["competitor_not_found"] = True
        return redirect(url_for("current_voting"), theme_id=theme_id)
    has_voted = vote_dao.has_voted(competition_id, session["user_id"])
    voted_name = vote_dao.get_voted_competitor_name(competition_id, user_id)
    # Default flags
    is_site_wide_banned = False
    is_banned = False

    is_site_wide_banned, is_banned = vote_dao.check_ban(user_id, theme_id)

    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.VOTING.value)
    return render_template(
        "competition/competitor_details.html",
        competitor=competitor,
        has_voted=has_voted,
        voted_name=voted_name,
        is_banned=is_banned,
        is_site_wide_banned=is_site_wide_banned
    )

# vote function
@app.route("/theme/<int:theme_id>/voter/vote", methods=["POST"])
def vote(theme_id):
    competition_id = session.get("competition_id")
    competitor_id = session.get("competitor_id")
    voter_id = session.get("user_id")

    if not competition_id or not competitor_id or not voter_id:
        session["vote_error"] = "Voting session data is missing."
        return redirect(url_for("current_voting"), theme_id=theme_id)

    competition_competitor_id = competition_dao.get_competition_competitor_id(
        competition_id, competitor_id
    )
    if not competition_competitor_id:
        session["vote_error"] = "Invalid voting data."
        return redirect(url_for("current_voting"), theme_id=theme_id)
    success, message = vote_dao.record_vote(
        competition_competitor_id, voter_id, request.remote_addr
    )
    session["vote_result"] = message
    return redirect(
        url_for(
            "competitor_details",
            competition_id=competition_id,
            competitor_id=competitor_id,
            theme_id=theme_id
        )
    )

# competition admin: search users to promote user to admin or scrutineer
@app.route('/theme/<int:theme_id>/admin/promotion', methods=['GET'])
def promotion(theme_id):
    # Set the active page in the session
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.PROMOTION.value)
    
    # Retrieve the search queries from request arguments
    username_query = request.args.get('username', '').strip()
    email_query = request.args.get('email', '').strip()
    first_name_query = request.args.get('first_name', '').strip()
    last_name_query = request.args.get('last_name', '').strip()
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort_by = request.args.get('sort_by', 'username')
    order = request.args.get('order', 'asc')
    
    # Fetch the logged-in user ID to exclude them from search
    exclude_user_id = session.get('user_id', None)
    
    # Ensure exclude_user_id is provided
    if exclude_user_id is None:
        return "Error: No user logged in", 403
    
    # Fetch voters with pagination and filters
    try:
        voters, total_voters = user_dao.search_voters_with_pagination(
            theme_id=theme_id,
            username=username_query,
            email=email_query,
            first_name=first_name_query,
            last_name=last_name_query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order
        )
    except Exception as e:
        return f"Error fetching voters: {str(e)}", 500

    # Calculate total pages for pagination
    total_pages = (total_voters + per_page - 1) // per_page

    # Render the template and pass the necessary context
    return render_template('competition/promotion.html',
                           voters=voters,
                           theme_id=theme_id,
                           page=page,
                           total_pages=total_pages,
                           sort_by=sort_by,
                           order=order,
                           username_query=username_query,
                           email_query=email_query,
                           first_name_query=first_name_query,
                           last_name_query=last_name_query)



# competition admin: promote user to admin or scrutineer
@app.route('/theme/<int:theme_id>/admin/promotion/change_role/<int:user_id>', methods=['GET', 'POST'])
def change_role(theme_id, user_id):
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.PROMOTION.value)
    user_info, current_theme_role, current_community_role = user_dao.get_user_roles(user_id, theme_id)
    if request.method == 'POST':
        new_theme_role = request.form.get('role')
        new_community_role = request.form.get('community_role')
        try:
            user_dao.update_user_roles(user_id, theme_id, new_theme_role, new_community_role)
        except Exception as e:
            print(f"Error inserting/updating role: {e}")
            return redirect(url_for('change_role', theme_id=theme_id, user_id=user_id))
        return render_template('competition/change_role.html', user=user_info, current_role=new_theme_role, theme_id=theme_id, user_id=user_id, success=True)
    return render_template('competition/change_role.html', user=user_info, current_role=current_theme_role, current_community_role=current_community_role, theme_id=theme_id, user_id=user_id)
