from project693.dao.base_dao import BaseDAO
from project693.model.theme import Theme
from datetime import datetime


class ThemeDao(BaseDAO):
    def __init__(self) -> None:
        super().__init__()

    def get_theme_by_id(self, theme_id) -> Theme:
        """
        Search theme entity by theme id

        Args:
            theme_id (int): theme id.

        Returns:
            theme (Theme object): The theme object whose id equals theme_id.
        """
        sql = "select id, name, description, application_id from competition_themes where id = %s"
        row = self.execute_query(sql, (theme_id,))
        theme = Theme(
            row[0][0],
            row[0][1],
            row[0][2],
            row[0][3],
        )
        return theme

    def theme_application_list(self, user_id):
        processed_result = []
        admin_check_query = """
        SELECT role FROM users 
        WHERE id = %s
        """
        role_result = self.execute_query(admin_check_query, (user_id,))

        if role_result and role_result[0][0] == "siteadmin":
            query = """
            SELECT ta.id, ta.theme_name, ta.theme_description, ta.applicant_id, ta.applying_time, ta.status, ta.rejection_reason, ta.operator_id, ta.operator, ta.operation_time,u.username
            FROM theme_applications ta
            JOIN users u ON ta.applicant_id=u.id
            """
            result = self.execute_query(query)
        else:
            query = """
            SELECT ta.id, ta.theme_name, ta.theme_description, ta.applicant_id, ta.applying_time, ta.status, ta.rejection_reason, ta.operator_id, ta.operator, ta.operation_time,u.username
            FROM theme_applications ta
            JOIN users u ON ta.applicant_id=u.id
            WHERE applicant_id = %s
            """
            result = self.execute_query(query, (user_id,))

        for row in result:
            (
                id,
                theme_name,
                theme_description,
                applicant_id,
                applying_time,
                status,
                rejection_reason,
                operator_id,
                operator,
                operation_time,
                username,
            ) = row

            if status == "pending":
                status_str = "Pending"
            elif status == "rejected":
                status_str = "Rejected"
            elif status == "approved":
                status_str = "Approved"
            else:
                status_str = "Unknown"

            processed_result.append(
                {
                    "id": id,
                    "theme_name": theme_name,
                    "theme_description": theme_description,
                    "username": username,
                    "applicant_id": applicant_id,
                    "applying_time": applying_time,
                    "status": status_str,
                    "rejection_reason": rejection_reason,
                    "operator_id": operator_id,
                    "operator": operator,
                    "operation_time": operation_time,
                }
            )
        return processed_result

    def theme_create(
        self,
        theme_name: str,
        theme_description: str,
        applicant_id: int,
        applicant: str,
        applying_time: datetime,
        status: str,
        rejection_reason: str,
        operator_id: int,
        operator: str,
        operation_time: datetime,
    ) -> None:
        query = (
            "INSERT INTO theme_applications (theme_name, theme_description, applicant_id, applicant,applying_time,status,rejection_reason,operator_id,operator,operation_time)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        self.execute_non_query(
            query,
            (
                theme_name,
                theme_description,
                applicant_id,
                applicant,
                applying_time,
                status,
                rejection_reason,
                operator_id,
                operator,
                operation_time,
            ),
        )

    def theme_list(self) -> list[Theme]:
        query = "select id, name, description, application_id from competition_themes"
        result = self.execute_query(query)
        Theme_list = [Theme(row[0], row[1], row[2], row[3]) for row in result]
        return Theme_list

    def theme_update(self, id: int, theme_name: str, theme_description: str) -> None:
        query = (
        "UPDATE theme_applications "
        "SET theme_name = %s, theme_description = %s "
        "WHERE id = %s"
        )
        self.execute_non_query(query, (theme_name, theme_description, id))

    def reject_theme(self, id: int, status: str, rejection_reason: str, operator_id: int, operator: str, operation_time: datetime) -> None:
        query = (
        "UPDATE theme_applications "
        "SET status = %s, rejection_reason = %s, operator_id = %s, operator = %s, operation_time = %s"
        "WHERE id = %s"
        )
        self.execute_non_query(query, (status, rejection_reason, operator_id, operator, operation_time,id))

    def approve_theme(self, theme_id: int, status: str, operator_id: int, operator: str, operation_time: datetime, theme_name: str, description: str, applicant_id: int,donation_status:str,donation_app_id:int) -> None:
        # 1. Update the theme's status in the `theme_applications` table
        update_theme_query = (
        "UPDATE theme_applications "
        "SET status = %s, operator_id = %s, operator = %s, operation_time = %s "
        "WHERE id = %s")
        # 2. Insert the new theme into the `competition_themes` table
        insert_competition_theme_query = (
        "INSERT INTO competition_themes (name, description, application_id,donation_status,donation_app_id) "
        "VALUES (%s, %s, %s,%s,%s)")
        # 3. Insert the admin role into the `user_theme_role` table
        insert_user_theme_role_query = (
        "INSERT INTO user_theme_role (theme_id, user_id, role) "
        "VALUES (LAST_INSERT_ID(), %s, 'admin')")
        # Prepare the queries and parameters to be executed as a transaction
        donation_app_id = donation_app_id if donation_app_id is not None else None

        queries_and_params = [
        (update_theme_query, (status, operator_id, operator, operation_time, theme_id)),
        (insert_competition_theme_query, (theme_name, description, applicant_id,donation_status,donation_app_id)),
        (insert_user_theme_role_query, (applicant_id,))]
        # Use the `execute_transaction` method to execute all queries atomically
        self.execute_transaction(queries_and_params)

    def theme_name_check(self,theme_name):
        query = "SELECT * FROM competition_themes WHERE name = %s"
        result = self.execute_query(query, (theme_name,))
        if result:
            return True 
        else:
            return None  