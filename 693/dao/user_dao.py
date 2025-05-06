from flask import session
from prototype.dao.base_dao import BaseDAO
from prototype.dao.theme_dao import ThemeDao
from prototype.model import User
from prototype.model import enums
from prototype.model.privacy_settings import UserPrivacySettings
from prototype.utils.hash_utils import get_password_hash
from prototype.model.enums import (
    Role,
    Status,
    CompetitionRole,
    VotingPermission,
    CommunityRole,
)
import json


class UserDao(BaseDAO):
    def __init__(self) -> None:
        super().__init__()

    def authenticate_user(self, user_name, password):
        query = (
            r"select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status, voting_permission"
            " from users where username = %s and password_hash = %s"
        )

        result = self.execute_query(query, (user_name, get_password_hash(password)))
        if len(result) > 0:
            # Convert role, status, and voting_permission to enums
            role_enum = enums.Role[result[0][9].upper()]
            status_enum = enums.Status[result[0][10].upper()]
            voting_permission_enum = enums.VotingPermission[result[0][11].upper()]

            # Create the User object
            user = User(
                id=result[0][0],
                username=result[0][1],
                password_hash=result[0][2],
                email=result[0][3],
                first_name=result[0][4],
                last_name=result[0][5],
                location=result[0][6],
                description=result[0][7],
                avatar=result[0][8],
                role=role_enum,  # Pass role as enum
                status=status_enum,  # Pass status as enum
                voting_permission=voting_permission_enum,  # Pass voting_permission as enum
                theme_role_mapping=None,  # This will be set later
                community_role_mapping=None,  # This will be set later
            )

            if user.status == enums.Status.ACTIVE:
                # Fetch competition permission data
                query = "select theme_id, role from user_theme_role where user_id = %s"
                result = self.execute_query(query, (user.id,))
                theme_role_mapping = {
                    row[0]: CompetitionRole[row[1].upper()] for row in result
                }
                user.theme_role_mapping = theme_role_mapping

                # Fetch community permission data
                query = (
                    "select theme_id, role from user_community_role where user_id = %s"
                )
                result = self.execute_query(query, (user.id,))
                community_role_mapping = {
                    row[0]: CommunityRole[row[1].upper()] for row in result
                }
                user.community_role_mapping = community_role_mapping

                return user, ""
            else:
                return (
                    None,
                    "Your account has been deactivated. Please contact an admin.",
                )
        else:
            return None, "Invalid username or password, please try again!"

    def get_user_details(self, user_id):
        query = (
            r"select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status, voting_permission"
            " from users where id = %s"
        )

        result = self.execute_query(query, (user_id,))
        if len(result) > 0:
            # Convert role, status, and voting_permission to enums
            role_enum = enums.Role[result[0][9].upper()]
            status_enum = enums.Status[result[0][10].upper()]
            voting_permission_enum = enums.VotingPermission[result[0][11].upper()]

            # Create the User object
            user = User(
                id=result[0][0],
                username=result[0][1],
                password_hash=result[0][2],
                email=result[0][3],
                first_name=result[0][4],
                last_name=result[0][5],
                location=result[0][6],
                description=result[0][7],
                avatar=result[0][8],
                role=role_enum,  # Pass role as enum
                status=status_enum,  # Pass status as enum
                voting_permission=voting_permission_enum,  # Pass voting_permission as enum
                theme_role_mapping=None,  # This will be set later
                community_role_mapping=None,  # This will be set later
            )

            # Fetch competition permission data
            query = "select theme_id, role from user_theme_role where user_id = %s"
            result = self.execute_query(query, (user.id,))
            theme_role_mapping = {
                row[0]: CompetitionRole[row[1].upper()] for row in result
            }
            user.theme_role_mapping = theme_role_mapping

            # Fetch community permission data
            query = "select theme_id, role from user_community_role where user_id = %s"
            result = self.execute_query(query, (user.id,))
            community_role_mapping = {
                row[0]: CommunityRole[row[1].upper()] for row in result
            }
            user.community_role_mapping = community_role_mapping

            return user

    def register(self, user: User):
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (user.username,))
        if len(result) > 0:
            return False, "User name '" + user.username + "' already exists."

        query = (
            "INSERT INTO users (username, password_hash, email, first_name, last_name, location, description, avatar, role, status)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        self.execute_non_query(
            query,
            (
                user.username,
                user.password_hash,
                user.email,
                user.first_name,
                user.last_name,
                user.location,
                user.description,
                user.avatar,
                user.role.value,
                user.status.value,
            ),
        )

        return (
            True,
            "User '" + user.username + "' registered successfully, please log in.",
        )

    def set_voter_status(self, voter_id, status):
        query = "UPDATE users SET status = %s WHERE id = %s"
        self.execute_non_query(query, (status, voter_id))

    def set_voter_role(self, voter_id, role):
        query = "UPDATE users SET role = %s WHERE id = %s"
        self.execute_non_query(query, (role, voter_id))

    def find_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        result = self.execute_query(query, (email,))

        if len(result) > 0:
            row = result[0]

            # Access values using tuple indices
            return User(
                id=row[0],  # 'id' column
                username=row[1],  # 'username' column
                password_hash=row[2],  # 'password_hash' column
                email=row[3],  # 'email' column
                first_name=row[4],  # 'first_name' column
                last_name=row[5],  # 'last_name' column
                location=row[6],  # 'location' column
                description=row[7],  # 'description' column
                avatar=row[8],  # 'avatar' column
                role=Role[row[9].upper()],  # Convert string to Role enum
                status=Status[row[10].upper()],  # Convert string to Status enum
                voting_permission=VotingPermission[
                    row[11].upper()
                ],  # Convert string to VotingPermission enum
                theme_role_mapping=None,  # Set theme_role_mapping to None
                community_role_mapping=None,
            )
        return None

    def find_by_id(self, user_id):
        query = "select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status,voting_permission from users where id = %s"
        result = self.execute_query(query, (user_id,))

        if result:
            user_data = result[0]
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=enums.Role(user_data[9]),
                status=enums.Status(user_data[10]),
                voting_permission=enums.VotingPermission(user_data[11]),
                theme_role_mapping=None,
                community_role_mapping=None,
            )

        return None

    def update_user(self, user: User):
        query = (
            "update users set username = %s, password_hash = %s, email = %s, first_name = %s, last_name = %s, "
            "location = %s, description = %s, avatar = %s, role = %s, status = %s where id = %s"
        )
        self.execute_non_query(
            query,
            (
                user.username,
                user.password_hash,
                user.email,
                user.first_name,
                user.last_name,
                user.location,
                user.description,
                user.avatar,
                user.role.value,
                user.status.value,
                user.id,
            ),
        )

    def search_backend_user(
        self, username, first_name, last_name, exclude_user=None
    ) -> list[User]:
        query = """
            SELECT id, username, email, first_name, last_name, role, status 
            FROM users 
            WHERE (role = 'admin' or role = 'scrutineer')
            """
        conditions = []
        parameters = []
        if username != "":
            conditions.append("username like %s")
            parameters.append(f"{username}%")

        if first_name != "":
            conditions.append("first_name like %s")
            parameters.append(f"%{first_name}%")

        if last_name != "":
            conditions.append("last_name like %s")
            parameters.append(f"%{last_name}%")

        if exclude_user:
            conditions.append("id != %s")
            parameters.append(exclude_user)

        sql = self.build_query(query, conditions)

        result = self.execute_query(sql, parameters)

        user_list = []
        for row in result:
            user = User(
                row[0],
                row[1],
                None,
                row[2],
                row[3],
                row[4],
                None,
                None,
                None,
                row[5],
                row[6],
            )
            user_list.append(user)

        return user_list

    def update_role(self, user_id, role: enums.Role):
        query = "UPDATE users SET role = %s WHERE id = %s"
        self.execute_non_query(query, (role.value, user_id))

    def update_status(self, user_id, status: enums.Status):
        query = "UPDATE users SET status = %s WHERE id = %s"
        self.execute_non_query(query, (status.value, user_id))

    def backend_user_add(self):
        # Generate unique username, email, and other default values
        last_user = self.execute_query("SELECT MAX(id) FROM users", ())[0][0] or 0
        username = f"backend_user_{last_user + 1}"
        email = f"{username}@example.com"
        password_hash = get_password_hash("backenduser1pass")
        first_name = "firstname"
        last_name = "lastname"
        location = "location"
        description = "n/a"
        avatar = "default.png"
        role = Role.SCRUTINEER.value
        status = Status.INACTIVE.value

        query = (
            "INSERT INTO users (username, password_hash, email, first_name, last_name, description, location, avatar, role, status)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )

        try:
            self.execute_non_query(
                query,
                (
                    username,
                    password_hash,
                    email,
                    first_name,
                    last_name,
                    description,
                    location,
                    avatar,
                    role,
                    status,
                ),
            )
            return True, f"Backend user '{username}' created successfully."
        except Exception as e:
            return False, f"Failed to create backend user: {str(e)}"

    def update_backend_user(
        self,
        user_id,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        location=None,
        description=None,
    ):
        query = "UPDATE users SET "
        params = []

        if username is not None:
            query += "username = %s, "
            params.append(username)
        if email is not None:
            query += "email = %s, "
            params.append(email)
        if first_name is not None:
            query += "first_name = %s, "
            params.append(first_name)
        if last_name is not None:
            query += "last_name = %s, "
            params.append(last_name)
        if location is not None:
            query += "location = %s, "
            params.append(location)
        if description is not None:
            query += "description = %s, "
            params.append(description)

        query = query.rstrip(", ")
        query += " WHERE id = %s"
        params.append(user_id)

        self.execute_non_query(query, params)

    def find_by_username(self, username):
        query = """
            SELECT id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status 
            FROM users 
            WHERE username = %s
        """
        result = self.execute_query(query, (username,))
        if result:
            user_data = result[0]
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=enums.Role(user_data[9]),
                status=enums.Status(user_data[10]),
            )
        return None

    def search_voters(self, username=None, email=None, first_name=None, last_name=None):
        query = """
            SELECT id, username, email, first_name, last_name, role, status, avatar, voting_permission
            FROM users
            WHERE 1 = 1
        """
        parameters = []

        if username:
            query += " AND username LIKE %s"
            parameters.append(f"%{username}%")

        if email:
            query += " AND email LIKE %s"
            parameters.append(f"%{email}%")

        if first_name:
            query += " AND first_name LIKE %s"
            parameters.append(f"%{first_name}%")

        if last_name:
            query += " AND last_name LIKE %s"
            parameters.append(f"%{last_name}%")

        result = self.execute_query(query, tuple(parameters))

        return [
            User(
                id=row[0],
                username=row[1],
                password_hash=None,
                email=row[2],
                first_name=row[3],
                last_name=row[4],
                location=None,
                description=None,
                avatar=row[7],
                role=Role[row[5].upper()],
                status=Status[row[6].upper()],
                voting_permission=VotingPermission[row[8].upper()],
                theme_role_mapping=None,
                community_role_mapping=None,
            )
            for row in result
        ]

    def get_full_user_info(self, user_id):
        query = """
            SELECT id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status, voting_permission
            FROM users
            WHERE id = %s
        """
        result = self.execute_query(query, (user_id,))

        if result:
            user_data = result[0]
            role_str = user_data[9]
            role = enums.Role[role_str.upper()]
            voting_permission_str = user_data[11]
            voting_permission = enums.VotingPermission[voting_permission_str.upper()]
            status_str = user_data[10]
            status = enums.Status[status_str.upper()]

            theme_role_mapping = {}
            role_query = "SELECT theme_id, role FROM user_theme_role WHERE user_id = %s"
            role_result = self.execute_query(role_query, (user_id,))
            theme_dao = ThemeDao()
            for row in role_result:
                theme = theme_dao.get_theme_by_id(row[0])
                theme_role_mapping[(theme.id, theme.name)] = enums.CompetitionRole[
                    row[1].upper()
                ]

            community_role_mapping = {}
            role_query = (
                "SELECT theme_id, role FROM user_community_role WHERE user_id = %s"
            )
            role_result = self.execute_query(role_query, (user_id,))
            for row in role_result:
                theme = theme_dao.get_theme_by_id(row[0])
                community_role_mapping[(theme.id, theme.name)] = enums.CommunityRole[
                    row[1].upper()
                ]

            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=role,
                status=status,
                voting_permission=voting_permission,
                theme_role_mapping=theme_role_mapping,
                community_role_mapping=community_role_mapping,
            )
        return None

    # List of Banned Competitions
    def banned_competitions(self, user_id):  # Jeremy
        query = """
                SELECT bv.theme_id, 
                ba.status AS appeal_status, 
                ba.upholding_reason,
                ct.name AS theme_name,
                bv.id
                FROM banned_voters bv
                LEFT JOIN ban_appeals ba ON bv.appeal_id = ba.id
                JOIN competition_themes ct ON bv.theme_id = ct.id
                WHERE bv.user_id = %s;
                """
        result = self.execute_query(query, (user_id,))

        # Query to check if the user is site-wide banned and check for any site-wide ban appeal
        sitewide_query = """
                        SELECT u.voting_permission, 
                        ba.theme_id, ba.status AS appeal_status, ba.upholding_reason, 
                        ba.id AS appeal_id
                        FROM users u
                        LEFT JOIN ban_appeals ba 
                        ON ba.id = u.appeal_id 
                        AND ba.ban_scope = 'sitewide'
                        WHERE u.id = %s;
                        """
        sitewide_result = self.execute_query(sitewide_query, (user_id,))

        # If the user is site-wide banned
        if sitewide_result and sitewide_result[0][0] == "banned":
            theme_id = sitewide_result[0][1]  # This will be None for site-wide bans
            appeal_status = sitewide_result[0][2] or ""
            upholding_reason = sitewide_result[0][3] or ""
            appeal_id = sitewide_result[0][4] or ""

            # Append the site-wide ban entry with the appeal information
            sitewide_ban = (
                theme_id,
                appeal_status,
                upholding_reason,
                "Site-Wide",
                appeal_id,
            )
            result.append(sitewide_ban)

        # Ensure all appeal_status and upholding_reason are not None in the theme-specific result
        result = [(r[0], r[1] or "", r[2] or "", r[3], r[4]) for r in result]

        return result

    def appeal(self, id, theme_id, user_id, username, appeal_reason):  # Jeremy
        query = """
                INSERT INTO ban_appeals (ban_scope, theme_id, appealer_id, appealer, appeal_reason, appeal_time, status)
                VALUES ('theme', %s, %s, %s, %s, NOW(), 'pending')
                """
        appeal_id = self.execute_non_query(
            query, (theme_id, user_id, username, appeal_reason)
        )

        query = """
            update banned_voters set appeal_id = %s where id = %s
            """
        self.execute_non_query(
            query,
            (
                appeal_id,
                id,
            ),
        )

    def appeal_sitewide(self, user_id, username, appeal_reason):  # Jeremy
        query = """
                INSERT INTO ban_appeals (ban_scope, theme_id, appealer_id, appealer, appeal_reason, appeal_time, status)
                VALUES ('sitewide', NULL, %s, %s, %s, NOW(), 'pending')
                """
        appeal_id = self.execute_non_query(query, (user_id, username, appeal_reason))

        query = """
            update users set appeal_id = %s where id = %s
            """
        self.execute_non_query(
            query,
            (
                appeal_id,
                user_id,
            ),
        )

    def get_ban_count(self, user_id):
        sql = """
            SELECT 
            (SELECT COUNT(*) 
            FROM banned_voters bv
            LEFT JOIN ban_appeals ba ON bv.appeal_id = ba.id
            WHERE bv.user_id = %s AND (ba.status IS NULL OR ba.status = 'upheld')
            ) +
            (SELECT COUNT(*)
            FROM users u
            LEFT JOIN ban_appeals ba ON u.appeal_id = ba.id AND ba.ban_scope = 'sitewide'
            WHERE u.id = %s AND u.voting_permission = 'banned' AND (ba.status IS NULL OR ba.status = 'upheld')
            ) AS total_ban_count
            """
        result = self.execute_query(sql, (user_id, user_id))
        return result[0][0] if result else 0

    # competition admin: search users to promote user to admin or scrutineer
    def search_voters_with_pagination(
        self,
        theme_id,
        username="",
        email="",
        first_name="",
        last_name="",
        page=1,
        per_page=10,
        sort_by="username",
        order="asc",
    ):
        offset = (page - 1) * per_page

        # Main query for fetching voters
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name,
                COALESCE(utr.role, 'voter') AS theme_role,
                COALESCE(ucr.role, 'voter') AS community_role
            FROM users AS u
            LEFT JOIN user_theme_role AS utr ON u.id = utr.user_id AND utr.theme_id = %s
            LEFT JOIN user_community_role AS ucr ON u.id = ucr.user_id AND ucr.theme_id = %s
            WHERE u.role = 'voter' AND u.id != %s
        """
        params = [theme_id, theme_id, session["user_id"]]

        # Apply search filters if provided
        if username:
            query += " AND u.username LIKE %s"
            params.append(f"%{username}%")
        if email:
            query += " AND u.email LIKE %s"
            params.append(f"%{email}%")
        if first_name:
            query += " AND u.first_name LIKE %s"
            params.append(f"%{first_name}%")
        if last_name:
            query += " AND u.last_name LIKE %s"
            params.append(f"%{last_name}%")

        # Add sorting, pagination, and execute the query
        query += f" ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
        params += [per_page, offset]
        voters = self.execute_query(query, tuple(params))

        # Count query for pagination
        count_query = """
            SELECT COUNT(*)
            FROM users AS u
            LEFT JOIN user_theme_role AS utr ON u.id = utr.user_id AND utr.theme_id = %s
            LEFT JOIN user_community_role AS ucr ON u.id = ucr.user_id AND ucr.theme_id = %s
            WHERE u.role = 'voter' AND u.id != %s
        """
        count_params = [theme_id, theme_id, session["user_id"]]

        # Apply same search filters for the count query
        if username:
            count_query += " AND u.username LIKE %s"
            count_params.append(f"%{username}%")
        if email:
            count_query += " AND u.email LIKE %s"
            count_params.append(f"%{email}%")
        if first_name:
            count_query += " AND u.first_name LIKE %s"
            count_params.append(f"%{first_name}%")
        if last_name:
            count_query += " AND u.last_name LIKE %s"
            count_params.append(f"%{last_name}%")

        # Execute the count query to get the total number of voters
        total_voters = self.execute_query(count_query, tuple(count_params))[0][0]

        return voters, total_voters

    # competition admin: promote user to admin or scrutineer
    def get_user_roles(self, user_id, theme_id):
        query = "SELECT username, email, first_name, last_name, location, description, avatar FROM users WHERE id = %s"
        user_info = self.execute_query(query, (user_id,))
        current_theme_role = self.execute_query(
            "SELECT role FROM user_theme_role WHERE user_id = %s AND theme_id = %s",
            (user_id, theme_id),
        )
        current_theme_role = current_theme_role[0][0] if current_theme_role else "voter"
        current_community_role = self.execute_query(
            "SELECT role FROM user_community_role WHERE user_id = %s AND theme_id = %s",
            (user_id, theme_id),
        )
        current_community_role = (
            current_community_role[0][0] if current_community_role else "voter"
        )
        return user_info[0], current_theme_role, current_community_role

    def update_user_roles(self, user_id, theme_id, new_theme_role, new_community_role):
        if new_theme_role == "voter":
            self.execute_non_query(
                "DELETE FROM user_theme_role WHERE user_id = %s AND theme_id = %s",
                (user_id, theme_id),
            )
        else:
            existing_role = self.execute_query(
                "SELECT role FROM user_theme_role WHERE user_id = %s AND theme_id = %s",
                (user_id, theme_id),
            )
            if existing_role:
                self.execute_non_query(
                    "UPDATE user_theme_role SET role = %s WHERE user_id = %s AND theme_id = %s",
                    (new_theme_role, user_id, theme_id),
                )
            else:
                self.execute_non_query(
                    "INSERT INTO user_theme_role (user_id, theme_id, role) VALUES (%s, %s, %s)",
                    (user_id, theme_id, new_theme_role),
                )
        if new_community_role == "voter":
            self.execute_non_query(
                "DELETE FROM user_community_role WHERE user_id = %s AND theme_id = %s",
                (user_id, theme_id),
            )
        else:
            existing_comm_role = self.execute_query(
                "SELECT role FROM user_community_role WHERE user_id = %s AND theme_id = %s",
                (user_id, theme_id),
            )
            if existing_comm_role:
                self.execute_non_query(
                    "UPDATE user_community_role SET role = %s WHERE user_id = %s AND theme_id = %s",
                    (new_community_role, user_id, theme_id),
                )
            else:
                self.execute_non_query(
                    "INSERT INTO user_community_role (user_id, theme_id, role) VALUES (%s, %s, %s)",
                    (user_id, theme_id, new_community_role),
                )

    # siteadmin: search to update user status active/inactive
    def search_users_with_pagination(
        self,
        exclude_user_id,
        username="",
        email="",
        first_name="",
        last_name="",
        page=1,
        per_page=10,
        sort_by="username",
        order="asc",
    ):
        offset = (page - 1) * per_page
        query = """
            SELECT u.id, u.username, u.email, u.first_name, u.last_name, u.role, u.status
            FROM users AS u
            WHERE u.id != %s
        """
        params = [exclude_user_id]
        if username:
            query += " AND u.username LIKE %s"
            params.append(f"%{username}%")
        if email:
            query += " AND u.email LIKE %s"
            params.append(f"%{email}%")
        if first_name:
            query += " AND u.first_name LIKE %s"
            params.append(f"%{first_name}%")
        if last_name:
            query += " AND u.last_name LIKE %s"
            params.append(f"%{last_name}%")
        query += f" ORDER BY {sort_by} {order} LIMIT %s OFFSET %s"
        params += [per_page, offset]
        voters = self.execute_query(query, tuple(params))
        count_query = """
            SELECT COUNT(*)
            FROM users AS u
            WHERE u.id != %s
        """
        count_params = [exclude_user_id]
        if username:
            count_query += " AND u.username LIKE %s"
            count_params.append(f"%{username}%")
        if email:
            count_query += " AND u.email LIKE %s"
            count_params.append(f"%{email}%")
        if first_name:
            count_query += " AND u.first_name LIKE %s"
            count_params.append(f"%{first_name}%")
        if last_name:
            count_query += " AND u.last_name LIKE %s"
            count_params.append(f"%{last_name}%")
        total_voters = self.execute_query(count_query, tuple(count_params))[0][0]
        return voters, total_voters

    def get_privacy_settings_by_id(self, user_id):
        sql = """
            select id, user_id, show_email, show_first_name, show_last_name, show_location, 
            show_description, show_avatar, show_recent_post, show_recent_vote, show_recent_donation, show_in_user_list		
            from user_privacy_settings
            where user_id = %s
        """
        result = self.execute_query(sql, (user_id,))
        userPrivacySettings = None
        if len(result) > 0:
            userPrivacySettings = UserPrivacySettings(
                result[0][0],
                result[0][1],
                result[0][2],
                result[0][3],
                result[0][4],
                result[0][5],
                result[0][6],
                result[0][7],
                result[0][8],
                result[0][9],
                result[0][10],
                result[0][11],
            )
        return userPrivacySettings

    def update_privacy_setting(self, privacy_settings):
        delete_sql = """
            DELETE FROM user_privacy_settings 
            WHERE user_id = %s;
        """
        parameters = []
        parameters.append((delete_sql, (privacy_settings.user_id,)))

        insert_sql = """
            INSERT INTO user_privacy_settings (user_id, show_email, show_first_name, show_last_name, 
                                                show_location, show_description, show_avatar, 
                                                show_recent_post, show_recent_vote, show_recent_donation,show_in_user_list)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);
        """
        parameters.append(
            (
                insert_sql,
                (
                    privacy_settings.user_id,
                    privacy_settings.show_email,
                    privacy_settings.show_first_name,
                    privacy_settings.show_last_name,
                    privacy_settings.show_location,
                    privacy_settings.show_description,
                    privacy_settings.show_avatar,
                    privacy_settings.show_recent_post,
                    privacy_settings.show_recent_vote,
                    privacy_settings.show_recent_donation,
                    privacy_settings.show_in_user_list,
                ),
            )
        )

        self.execute_transaction(parameters)
