from flask import session
from enum import Enum


class SessionManager:
    # Session keys as constants
    USER = "user"
    ACTIVE_PAGE = "active_page"

    class Page(Enum):
        HOME = "home"
        VOTING = "current_voting"
        COMPETITION_RESULTS = "competition_results"
        LOGIN = "login"
        COMPETITION_SETUP = "competition_setup"
        COMPETITOR_SETUP = "competitor_setup"
        MANAGING_USER = "managing_user"
        SCRUTINEERING = "scrutineering"
        MANAGING_VOTER = "managing_voter"
        ANNOUNCEMENT_SETUP = "announcement_setup"
        USER_PROFILE = "user_profile"
        CHANGE_PASSWORD = "change_password"
        PROMOTION = "promotion"
        SITEHOME = "site_home"
        ABOUTUS = "about_us"
        BANNED_COMPETITIONS = "banned_competitions"
        PRIVACYSETTINGS = "privacy_settings"
        VOTING_INTEGRITY = "voting_integrity"
        MY_COMPETITION_APPLICATION = "my_competition_application"
        MY_DONATION = "my_donation"
        MY_BAN = "my_ban"
        MANAGING_COMPETITION_APPLICATION = "managing_competition_application"
        MANAGING_DONATION_APPLICATION = "managing_donation_application"
        SITEWIDE_APPEAL_REQUESTS = "sitewide_appeal_requests"
        ALL_POST = "all_post"
        MY_POST = "my_post"
        CREATE_POST = "create_post"
        DAILY_VOTES = "daily_votes"
        LIST_OF_VOTES = "list_of_votes"
        LIST_OF_VOTERS = "list_of_voters"
        BAN_APPEAL_REQUESTS = "ban_appeal_requests"
        APPROVING_COMPETITION = "approving_competition"
        DONATION_HOME = "donation_home"
        DONATION_APPLICATION_HISTORY = "donation_application_history"
        DONATION_REPORT = "donation_report"

    @staticmethod
    def set(key, value):
        """set session variable"""
        session[key] = value

    @staticmethod
    def get(key):
        """get session variable"""
        return session.get(key)

    @staticmethod
    def remove(key):
        """remove session variable"""
        if key in session:
            del session[key]

    @staticmethod
    def clear():
        """clear all session variable"""
        session.clear()
