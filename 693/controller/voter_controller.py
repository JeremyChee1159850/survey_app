from flask import Flask, render_template, request, redirect, url_for, session, flash
from prototype.dao.user_dao import UserDao
from prototype.dao.base_dao import BaseDAO
from prototype.model import User
from prototype.utils.session_manager import SessionManager
from prototype.model.enums import Role, Status
from prototype.controller import app

user_dao = UserDao()

# siteadmin: search to update user status active/inactive
@app.route('/siteadmin/managing_voter', methods=['GET'])
def managing_voter():
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.MANAGING_VOTER.value)
    username_query = request.args.get('username', '').strip()
    email_query = request.args.get('email', '').strip()
    first_name_query = request.args.get('first_name', '').strip()
    last_name_query = request.args.get('last_name', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    sort_by = request.args.get('sort_by', 'username')
    order = request.args.get('order', 'asc')
    valid_columns = ['username', 'email', 'first_name', 'last_name', 'role', 'status']
    if sort_by not in valid_columns:
        sort_by = 'username'
    if order not in ['asc', 'desc']:
        order = 'asc'
    voters, total_voters = user_dao.search_users_with_pagination(
        exclude_user_id=session['user_id'],
        username=username_query,
        email=email_query,
        first_name=first_name_query,
        last_name=last_name_query,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order
    )
    total_pages = (total_voters + per_page - 1) // per_page
    return render_template(
        'user/managing_voter.html',
        voters=voters,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
        username_query=username_query,
        email_query=email_query,
        first_name_query=first_name_query,
        last_name_query=last_name_query
    )


# siteadmin: view profile to update user status active/inactive
@app.route('/siteadmin/voter_profile/<int:user_id>', methods=['GET', 'POST'])
def voter_profile(user_id):
    user_dao = UserDao()
    voter = user_dao.get_full_user_info(user_id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        new_role = request.form.get('role')
        user_dao.set_voter_status(user_id, new_status)
        if new_role: 
            user_dao.set_voter_role(user_id, new_role)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('voter_profile', user_id=user_id))
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.MANAGING_VOTER.value)
    return render_template('user/voter_profile.html', voter=voter)