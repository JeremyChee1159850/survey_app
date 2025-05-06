from prototype.dao.base_dao import BaseDAO
from prototype.model.vote import Vote
from prototype.model.enums import VoteStatus
from datetime import datetime
import json


class VoteDao(BaseDAO):

    def __init__(self) -> None:
        super().__init__()

    def record_vote(self, competition_competitor_id, voter_id, voting_ip):
        query = """
            SELECT * FROM votes 
            WHERE competition_competitor_id = %s AND voter_id = %s
        """
        result = self.execute_query(query, (competition_competitor_id, voter_id))
        if result:
            return False, "You have already voted in this competition."

        query = """
            INSERT INTO votes (competition_competitor_id, voter_id, voting_time, voting_ip, status)
            VALUES (%s, %s, NOW(), %s, %s)
        """
        self.execute_non_query(
            query,
            (
                competition_competitor_id,
                voter_id,
                voting_ip,
                VoteStatus.VALID.value,
            ),
        )
        return True, "Vote recorded successfully."

    def has_voted(self, competition_id, voter_id):
        query = """
            SELECT v.id FROM votes v
            INNER JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            WHERE cc.competition_id = %s AND v.voter_id = %s
        """
        result = self.execute_query(query, (competition_id, voter_id))
        return len(result) > 0

    def get_recent_voters(self, competition_id):
        query = """
            SELECT u.avatar, u.username, u.description 
            FROM votes v
            JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            JOIN users u ON v.voter_id = u.id
            WHERE cc.competition_id = %s
            ORDER BY v.voting_time DESC
            LIMIT 10
        """
        return self.execute_query(query, (competition_id,))
    
    def check_ban(self, voter_id, theme_id): # Jeremy
        # First check if the user is site-wide banned
        query_site_wide_ban = """
            SELECT voting_permission
            FROM users
            WHERE id = %s
            LIMIT 1;
            """
        result_site_wide_ban = self.execute_query(query_site_wide_ban, (voter_id,))

        is_site_wide_banned = result_site_wide_ban and result_site_wide_ban[0][0] == 'banned'
        
        # If site-wide banned, no need to check theme-specific ban
        if is_site_wide_banned:
            return True, False

        # If not site-wide banned, check if the user is banned from the specific theme
        query_theme_ban = """
            SELECT 1
            FROM banned_voters
            WHERE user_id = %s AND theme_id = %s
            LIMIT 1;
            """
        result_theme_ban = self.execute_query(query_theme_ban, (voter_id, theme_id))
        is_banned = len(result_theme_ban) > 0
        return False, is_banned

    def get_voter_locations(self, competition_id):
        query = """
            SELECT u.location 
            FROM votes v
            JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            JOIN users u ON v.voter_id = u.id
            WHERE cc.competition_id = %s
        """
        results = self.execute_query(query, (competition_id,))
        voter_locations = []
        for row in results:
            location = json.loads(row[0]) if row[0] else {}
            if "lat" in location and "lon" in location: 
                voter_locations.append({"location_lat": location["lat"], "location_lon": location["lon"]})
        return voter_locations
    
    def get_voted_competitor_name(self, competition_id, voter_id):
        query = """
            SELECT comp.name
            FROM votes v
            INNER JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            INNER JOIN competitors comp ON cc.competitor_id = comp.id
            WHERE cc.competition_id = %s AND v.voter_id = %s
        """
        result = self.execute_query(query, (competition_id, voter_id))
        return result[0][0] if result else None