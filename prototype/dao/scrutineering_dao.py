from prototype.dao.base_dao import BaseDAO
from typing import Tuple, List
from datetime import datetime, timedelta


class ScrutineeringDAO(BaseDAO):

    def summary_votes(self, theme_id):
        query = (
            f"select a.name,a.voting_start_date,a.voting_end_date, DATE_FORMAT(c.voting_time,'%d-%m-%Y'),count(*)"
            " from competitions a "
            " inner join competition_competitors b on a.id = b.competition_id"
            " inner join votes c on b.id = c.competition_competitor_id"
            " where a.status = 'ongoing' and a.theme_id = %s"
            f" group by a.name,a.voting_start_date,a.voting_end_date,DATE_FORMAT(c.voting_time,'%d-%m-%Y')"
            f" order by DATE_FORMAT(c.voting_time,'%d-%m-%Y')"
        )
        return self.execute_query(query, (theme_id,))

    def generate_date_range(self, start_date, end_date):
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%d-%m-%Y"))
            current_date += timedelta(days=1)
        return dates

    def unusual_votes(self, competition_id, ip, theme_id):
        sql = """
            select a.status, a.id as competition_id, a.name as competition_name,
            c.id as vote_id, d.username as voter, c.voting_time, c.voting_ip,
            b.competitor_id, e.name as competitor_name,c.status as vote_status
            from competitions a
            inner join competition_competitors b on a.id = b.competition_id
            inner join votes c on b.id = c.competition_competitor_id
            inner join users d on c.voter_id = d.id
            inner join competitors e on b.competitor_id = e.id
            where a.status in ("ongoing", "ended")
            """

        conditions = []
        parameter = []
        conditions.append("a.theme_id = %s")
        parameter.append(theme_id)

        if competition_id != "":
            conditions.append("a.id = %s")
            parameter.append(competition_id)
        if ip != "":
            conditions.append("c.voting_ip like %s")
            parameter.append(f"%{ip}%")

        sql = self.build_query(sql, conditions) + " order by a.status,a.id,d.id"
        result = self.execute_query(sql, parameter)
        votes = [
            {
                "status": row[0],
                "competition_id": row[1],
                "competition_name": row[2],
                "vote_id": row[3],
                "voter": row[4],
                "voting_time": row[5].strftime("%d-%m-%Y %H:%M"),
                "voting_ip": row[6],
                "competitor_id": row[7],
                "competitor_name": row[8],
                "vote_status": row[9],
            }
            for row in result
        ]
        return votes

    def invalidate(self, ids):
        parms = ",".join(map(str, ids))
        sql = f"update votes set status = 'invalid' where id in({parms})"
        self.execute_non_query(sql)

    # Invalidate the votes of a specific voter in all ongoing and ended competition
    def invalidate_votes(self, voter_id):
        sql = """
            UPDATE votes v
            JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            JOIN competitions c ON cc.competition_id = c.id
            SET v.status = 'invalid'
            WHERE v.voter_id = %s AND c.status IN ('ongoing', 'ended')
            """
        self.execute_non_query(sql, (voter_id,))

    def deactivate(self, ids):  # Jeremy
        parms = ",".join(map(str, ids))
        sql = f"""UPDATE users SET status = 'inactive' WHERE id IN (SELECT voter_id FROM votes WHERE id IN ({parms}))"""
        self.execute_non_query(sql)

    def unusual_votes_by_ip(self, theme_id):  # Jeremy
        sql = """
            SELECT a.voting_ip, COUNT(a.id) AS vote_count
            FROM votes a
            JOIN competition_competitors b ON a.competition_competitor_id = b.id
            JOIN competitions c ON b.competition_id = c.id
            WHERE c.status IN ('ongoing', 'ended') and c.theme_id = %s
            GROUP BY a.voting_ip
            ORDER BY COUNT(a.id) DESC;
            """  
        
        result = self.execute_query(sql, (theme_id,))
    
        return [
            {"voting_ip": row[0], "vote_count": row[1]}
            for row in result
        ]
    
    def list_voters(self, username, first_name, last_name, theme_id, current_user_id): # Jeremy
        sql = """SELECT a.id, a.username, a.first_name, a.last_name, COUNT(b.id) AS number_of_votes,
               CASE WHEN bv.id IS NOT NULL THEN 1 ELSE 0 END AS is_banned
                FROM votes b
                JOIN users a ON b.voter_id = a.id
                JOIN competition_competitors c ON b.competition_competitor_id = c.id
                JOIN competitions d ON c.competition_id = d.id
                JOIN competition_themes e ON d.theme_id = e.id
                LEFT JOIN banned_voters bv ON a.id = bv.user_id AND bv.theme_id = e.id
                WHERE e.id = %s AND a.id != %s
                """
        
        parameters = [theme_id, current_user_id]
        
        if username:
            sql += " AND a.username LIKE %s"
            parameters.append(f"%{username}%")
        if first_name:
            sql += " AND a.first_name LIKE %s"
            parameters.append(f"%{first_name}%")
        if last_name:
            sql += " AND a.last_name LIKE %s"
            parameters.append(f"%{last_name}%")
        
        sql += " GROUP BY a.id, a.username, a.first_name, a.last_name, bv.id"
        sql += " ORDER BY is_banned ASC, number_of_votes DESC"

        result = self.execute_query(sql, parameters)
            
        voters = [
            {   
                "id": row[0],
                "username": row[1],
                "first_name": row[2],
                "last_name": row[3],
                "number_of_votes": row[4],
                "is_banned": row[5]
            }
            for row in result
        ]
        return voters
    
    def voter_details(self, voter_id, theme_id): # Jeremy
        sql = """SELECT a.name AS competition_name, b.name AS theme_name, c.name AS competitor_name, 
             v.voting_time, v.voting_ip 
             FROM votes v
             JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
             JOIN competitors c ON cc.competitor_id = c.id
             JOIN competitions a ON cc.competition_id = a.id
             JOIN competition_themes b ON a.theme_id = b.id
             WHERE v.voter_id = %s AND b.id = %s;
            """
        
        result = self.execute_query(sql, [voter_id, theme_id])
        
        votes = [
            {
                "competition_name": row[0],
                "theme_name": row[1],
                "competitor_name": row[2],
                "voting_time": row[3].strftime("%d-%m-%Y"),
                "voting_ip": row[4],
            }
            for row in result
        ]
        return votes
    
    def get_username_by_id(self, user_id):
        query = "SELECT username FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,))
        return result[0][0] if result else None
    
    def theme_ban(self, voter_id, theme_id):
        # Step 1: Create a new 'pending' appeal in the ban_appeals table
        appeal_query = """
                        INSERT INTO ban_appeals (ban_scope, theme_id, appealer_id, appealer, appeal_reason, appeal_time, status)
                        VALUES ('theme', %s, %s, %s, 'Automatic ban appeal', NOW(), 'pending')
                        """

        appealer_username = self.get_username_by_id(voter_id)
        self.execute_non_query(appeal_query, (theme_id, voter_id, appealer_username))
        
        # Step 2: Retrieve the appeal_id of the newly inserted appeal
        appeal_id_query = "SELECT LAST_INSERT_ID()"
        appeal_id_result = self.execute_query(appeal_id_query)
        appeal_id = appeal_id_result[0][0]

        # Step 3: Insert the ban into banned_voters table with the new appeal_id
        ban_query = """
            INSERT INTO banned_voters (user_id, theme_id, appeal_id)
            VALUES (%s, %s, %s)
            """
        self.execute_non_query(ban_query, (voter_id, theme_id, appeal_id))

    def site_wide_ban(self, voter_id): # Jeremy
         # Step 1: Create a new 'pending' appeal in the ban_appeals table for the site-wide ban
        appeal_query = """
                        INSERT INTO ban_appeals (ban_scope, theme_id, appealer_id, appealer, appeal_reason, appeal_time, status)
                        VALUES ('sitewide', NULL, %s, %s, 'Automatic site-wide ban appeal', NOW(), 'pending')
                        """

        appealer_username = self.get_username_by_id(voter_id)
        self.execute_non_query(appeal_query, (voter_id, appealer_username))
        # Step 2: Update the user's voting permission to 'banned'
        sql = "UPDATE users SET voting_permission = 'banned' WHERE id = %s"
        self.execute_non_query(sql, (voter_id,))

    def profile_voter(self, voter_id): # Jeremy
        query = """
            SELECT id, username, first_name, last_name, email, location, description
            FROM users
            WHERE id = %s
            """
        result = self.execute_query(query, (voter_id,))
        
        if result:
            return {
                "id": result[0][0],
                "username": result[0][1],
                "first_name": result[0][2],
                "last_name": result[0][3],
                "email": result[0][4],
                "location": result[0][5],
                "description": result[0][6]
            }
        return None

    def view_appeals(self, theme_id, selected_status='pending'): # Jeremy
        query = """
                SELECT id, ban_scope, theme_id, appealer, appeal_reason, appeal_time, status
                FROM ban_appeals
                WHERE theme_id = %s 
                AND ban_scope = 'theme' 
                AND appeal_reason != 'Automatic ban appeal'
                """
        params = [theme_id]

        if selected_status != 'all':
            query += " AND status = %s"
            params.append(selected_status)
        
        result = self.execute_query(query, tuple(params))
        
        appeals = [
            {
                "id": row[0],
                "ban_scope": row[1],
                "theme_id": row[2],
                "appealer": row[3],
                "appeal_reason": row[4],
                "appeal_time": row[5].strftime("%d-%m-%Y %H:%M"),
                "status": row[6]
            }
            for row in result
        ]
        return appeals
    
    def validate_votes(self, voter_id): # Jeremy
        sql = """
            UPDATE votes v
            JOIN competition_competitors cc ON v.competition_competitor_id = cc.id
            JOIN competitions c ON cc.competition_id = c.id
            SET v.status = 'valid'
            WHERE v.voter_id = %s AND c.status IN ('ongoing', 'ended')
            """
        self.execute_non_query(sql, (voter_id,))

    def appeal_details(self, appeal_id): # Jeremy
        sql = """
            SELECT appealer_id, ban_scope, theme_id, appeal_reason, status
            FROM ban_appeals
            WHERE id = %s
            """
        result = self.execute_query(sql, (appeal_id,))
        
        if result:
            return {
                "appealer_id": result[0][0],
                "ban_scope": result[0][1],
                "theme_id": result[0][2],
                "appeal_reason": result[0][3],
                "status": result[0][4]     
            }
        
        return None
    
    def update_appeal_status(self, appeal_id, new_status, operator_id, upholding_reason=None): # Jeremy
        query = """
                UPDATE ban_appeals
                SET status = %s, upholding_reason = %s, operator_id = %s, operation_time = NOW()
                WHERE id = %s
                """
        self.execute_non_query(query, (new_status, upholding_reason, operator_id, appeal_id))

    def remove_banned_voter(self, user_id, theme_id):
        sql = "DELETE FROM banned_voters WHERE user_id = %s AND theme_id = %s"
        self.execute_non_query(sql, (user_id, theme_id))

    def get_appeal_count(self, theme_id):
        sql = "SELECT COUNT(*) FROM ban_appeals WHERE status = 'pending' AND theme_id = %s AND appeal_reason != 'Automatic ban appeal'"
        result = self.execute_query(sql, (theme_id,))
        return result[0][0] if result else 0
    
    def sw_appeal_count(self):
        sql = """
            SELECT COUNT(*)
            FROM ban_appeals
            WHERE ban_scope = 'sitewide'
            AND appeal_reason != 'Automatic site-wide ban appeal'
            AND status = 'pending'
            """
        result = self.execute_query(sql)
        return result[0][0] if result else 0
    
    def voting_integrity(self):
        query = """
                SELECT u.id, u.username, COUNT(bv.id) AS ban_count, u.voting_permission
                FROM users u
                JOIN banned_voters bv ON u.id = bv.user_id
                GROUP BY u.id, u.username
                ORDER BY ban_count DESC;
                """

        result = self.execute_query(query)

        # Prepare list to store banned users and their voting activity
        banned_users = []
        for row in result:
            user_data = {
                "user_id": row[0],
                "username": row[1],
                "ban_count": row[2],  # Total votes cast by the banned user
                "voting_permission": row[3],
            }
            banned_users.append(user_data)

        return banned_users
    
    def banned_themes(self, user_id):
        query = """SELECT ct.name AS theme_name
                FROM banned_voters bv
                JOIN competition_themes ct ON bv.theme_id = ct.id
                WHERE bv.user_id = %s
                """
        result = self.execute_query(query, (user_id,))
        
        banned_themes = [{"theme_name": row[0]} for row in result]
        return banned_themes
    
    def sitewide_appeals(self, selected_status='pending'): # Jeremy
        query = """
                SELECT id, ban_scope, appealer, appeal_reason, appeal_time, status
                FROM ban_appeals
                WHERE ban_scope = 'sitewide'
                AND appeal_reason != 'Automatic site-wide ban appeal'
                """
        
        params = []

        if selected_status != 'all':
            query += " AND status = %s"
            params.append(selected_status)
        
        result = self.execute_query(query, tuple(params))
        
        sitewide_appeals = [
            {
                "id": row[0],
                "ban_scope": row[1],
                "appealer": row[2],
                "appeal_reason": row[3],
                "appeal_time": row[4].strftime("%d-%m-%Y %H:%M"),
                "status": row[5]
            }
            for row in result
        ]
        return sitewide_appeals
    
    def remove_sitewide_ban(self, voter_id):
         # Add a print or logging statement to check if this method is called
        print(f"Removing site-wide ban for voter_id: {voter_id}")
        # Logic to remove site-wide ban for the given voter
        query = "UPDATE users SET voting_permission = 'allowed' WHERE id = %s AND voting_permission = 'banned'"
        # Add a print or logging statement to check the exact query and parameter being executed
        print(f"Executing query: {query} with voter_id: {voter_id}")

        self.execute_non_query(query, (voter_id,))