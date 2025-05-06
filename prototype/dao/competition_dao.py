from prototype.dao.base_dao import BaseDAO
from prototype.model.competition import CompetitionResult
from prototype.model.competition import Competition
from prototype.model.competitor import Competitor
from prototype.model.competitor import CompetitionCompetitor
from typing import Tuple, Optional, List
from datetime import datetime
from prototype.dao.theme_dao import ThemeDao
from prototype.model.theme import Theme
import json


class CompetitionDao(BaseDAO):

    def __init__(self) -> None:
        super().__init__()

    def current_competition(self, status) -> List[Competition]:
        query = "SELECT * FROM competitions WHERE status = %s"
        current_competition = []
        result = self.execute_query(query, (status,))
        for row in result:
            competition = Competition(
                row[0],
                row[1],
                row[2].strftime("%d-%m-%Y %H:%M:%S"),
                row[3].strftime("%d-%m-%Y %H:%M:%S"),
                row[4],
            )
            competition.competitors = self.current_competitor(competition.id)
            current_competition.append(competition)

        return current_competition

    def current_competitor(self, competition_id) -> List[Competitor]:
        query = """
            SELECT c.id, c.name, c.description, c.image
            FROM competitors c
            INNER JOIN competition_competitors cc ON c.id = cc.competitor_id
            WHERE cc.competition_id = %s
        """
        current_competitor = []
        result = self.execute_query(query, (competition_id,))
        for row in result:
            competitor = Competitor(row[0], row[1], row[2], row[3])
            current_competitor.append(competitor)

        return current_competitor

    def get_competition_competitor_id(self, competition_id, competitor_id):
        query = """
            SELECT id FROM competition_competitors
            WHERE competition_id = %s AND competitor_id = %s
        """
        result = self.execute_query(query, (competition_id, competitor_id))
        if result:
            return result[0][0]
        return None

    def get_competitor_details(self, competitor_id) -> CompetitionCompetitor:
        query = """
            SELECT cc.competition_id, c.id, c.name, c.description, c.image, c.location, cc.vote_count, cc.vote_ratio, cc.is_winner
            FROM competitors c
            INNER JOIN competition_competitors cc ON c.id = cc.competitor_id
            WHERE c.id = %s
        """
        result = self.execute_query(query, (competitor_id,))
        if result:
            row = result[0]
            competitor = Competitor(
                id=row[1],
                name=row[2],
                description=row[3],
                image=row[4],
                location=row[5],
            )
            competition_competitor = CompetitionCompetitor(
                competition_id=row[0],
                competitor_id=row[1],
                vote_count=row[6],
                vote_ratio=row[7],
                is_winner=row[8],
            )
            return competition_competitor, competitor
        return None, None

    def all_finalized_competition_results(self) -> list:
        query = """SELECT c.id AS competition_id, c.name AS competition_name, comp.name AS competitor_name,
                    (SELECT SUM(cc2.vote_count) FROM competition_competitors cc2 WHERE cc2.competition_id = c.id) AS total_votes,
                    cc.vote_ratio AS winner_votes_proportion
                    FROM competition_competitors cc
                    JOIN competitions c ON cc.competition_id = c.id
                    JOIN competitors comp ON cc.competitor_id = comp.id
                    WHERE c.status = 'published'
                    AND cc.is_winner = 1
                    ORDER BY c.voting_end_date DESC, c.name, cc.vote_count DESC;"""

        results = self.execute_query(query)

        competition_results = []
        for row in results:
            competitionresult = CompetitionResult(
                row[0], row[1], row[2], row[3], row[4]
            )
            competition_results.append(competitionresult)

        return competition_results

    def competition_details(self, competition_id):
        query = """SELECT comp.id AS competitor_id, comp.name AS competitor_name, cc.vote_count AS total_votes,
                CONCAT(ROUND(cc.vote_ratio * 100, 1), '%') AS vote_percentage, comp.image AS image
                FROM competition_competitors cc JOIN competitors comp ON cc.competitor_id = comp.id
                WHERE cc.competition_id = %s ORDER BY cc.vote_count DESC;"""

        results = self.execute_query(query, (competition_id,))

        competition_details = []
        max_votes = 0
        for row in results:
            detail = {
                "competitor_id": row[0],
                "competitor_name": row[1],
                "total_votes": row[2],
                "vote_percentage": row[3],
                "image": row[4],
            }
            competition_details.append(detail)
            if row[2] > max_votes:
                max_votes = row[2]

        for detail in competition_details:
            detail["is_winner"] = detail["total_votes"] == max_votes

        return competition_details

    def competition_name(self, competition_id):
        """Fetches the competition name by ID."""
        query = "SELECT name FROM competitions WHERE id = %s"
        result = self.execute_query(query, (competition_id,))

        if result:
            return result[0][0]  # Return the name of the competition

    def search_competitions(self, status, theme_id) -> List[Competition]:
        if status == "all":
            query = "SELECT id, name, voting_start_date, voting_end_date, status FROM competitions where 'all' = %s and theme_id = %s order by status"
        else:
            query = "SELECT id, name, voting_start_date, voting_end_date, status FROM competitions WHERE status = %s and theme_id = %s order by status"
        current_competition = []
        result = self.execute_query(
            query,
            (
                status,
                theme_id,
            ),
        )
        for row in result:
            competition = Competition(
                row[0],
                row[1],
                row[2].strftime("%d-%m-%Y"),
                row[3].strftime("%d-%m-%Y"),
                row[4],
            )
            current_competition.append(competition)

        return current_competition

    def add_competition(self, name, voting_start_date, voting_end_date, theme_id):
        query = (
            "insert into competitions(name,voting_start_date, voting_end_date, status, theme_id, theme_name)"
            " values(%s,%s,%s,%s,%s,%s)"
        )

        themeDao = ThemeDao()
        theme = themeDao.get_theme_by_id(theme_id)
        self.execute_non_query(
            query,
            (name, voting_start_date, voting_end_date, "pending", theme_id, theme.name),
        )

    def del_competition(self, id):
        queries_and_params = [
            ("DELETE FROM competition_competitors WHERE competition_id = %s", (id,)),
            ("DELETE FROM competitions WHERE id = %s", (id,)),
        ]
        self.execute_transaction(queries_and_params)

    def get_competition_by_id(self, id) -> Competition:
        query = "SELECT id, name, voting_start_date, voting_end_date, status FROM competitions where id =%s "
        row = self.execute_query(query, (id,))
        competition = Competition(
            row[0][0],
            row[0][1],
            row[0][2],
            row[0][3],
            row[0][4],
        )
        return competition

    def edit_competition(self, id, name, voting_start_date, voting_end_date):
        query = "update competitions set name=%s, voting_start_date=%s, voting_end_date=%s where id = %s"
        self.execute_non_query(query, (name, voting_start_date, voting_end_date, id))

    def launch_competition(self, id, theme_id):
        query = "select * from competitions where status = 'ongoing' and theme_id=%s"
        result = self.execute_query(query, (theme_id,))
        if len(result) > 0:
            return (
                False,
                "An onging competition already exists, so you cannot launch another one.",
            )
        else:
            query = "update competitions set status='ongoing' where id =%s"
            self.execute_non_query(query, (id,))
            competition = self.get_competition_by_id(id)
            return True, "Competition %s has been successfully launched." % (
                competition.name
            )

    # 新增dao
    def add_competitor_to_competition(
        self,
        competition_id: int,
        competitor_id: int,
        vote_count: int = 0,
        vote_ratio: int = 0,
        is_winner: int = 0,
    ) -> None:
        query = """
        INSERT INTO competition_competitors (competition_id, competitor_id, vote_count, vote_ratio, is_winner)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_non_query(
            query, (competition_id, competitor_id, vote_count, vote_ratio, is_winner)
        )

    def get_competitors_by_competition(
        self, competition_id: int
    ) -> List[dict[str, any]]:
        query = """
        SELECT competitors.id, competitors.name
        FROM competition_competitors
        JOIN competitors ON competition_competitors.competitor_id = competitors.id
        WHERE competition_competitors.competition_id = %s
        """
        results = self.execute_query(query, (competition_id,))
        competitors = [{"id": row[0], "name": row[1]} for row in results]
        return competitors

    def get_competition_id_by_name(self, competition_name: str) -> int:
        query = "SELECT id FROM competitions WHERE name = %s"
        result = self.execute_query(query, (competition_name,))
        if result:
            return result[0][0]
        return None

    def get_competition_staus(self, competition_id: int):
        query = "SELECT status FROM competitions WHERE id = %s"
        result = self.execute_query(query, (competition_id,))
        if result:
            return result[0][0]
        return None

    def delete_competitor_from_competition(
        self, competition_id: int, competitor_id: int
    ) -> None:
        query = """DELETE FROM competition_competitors
                WHERE competition_id = %s AND competitor_id = %s
            """
        self.execute_non_query(query, (competition_id, competitor_id))

    def update_status_for_expired_competitions(self, specific_date):

        current_date = specific_date if specific_date else datetime.now().date()
        sql = """
            UPDATE competitions SET status = 'ended'
            WHERE status = 'ongoing' AND voting_end_date < %s;
        """
        parameters = [
            ("SET SQL_SAFE_UPDATES = %s;", (0,)),
            (sql, (current_date,)),
            ("SET SQL_SAFE_UPDATES = %s;", (1,)),
        ]

        self.execute_transaction(parameters)

        return "Competitions with an end date before {} have been ended".format(
            current_date
        )

    def ongoing_or_ended_competition(self, theme_id):
        query = """SELECT id, name AS competition_name, voting_start_date, voting_end_date, 
                status AS competition_status FROM competitions WHERE status IN ('ongoing', 'ended')
                and theme_id = %s
                ORDER BY status, name;"""
        result = self.execute_query(query, (theme_id,))
        competitions = [
            {
                "id": row[0],
                "competition_name": row[1],
                "voting_start_date": row[2].strftime("%d/%m/%Y") if row[2] else "",
                "voting_end_date": row[3].strftime("%d/%m/%Y") if row[3] else "",
                "competition_status": row[4],
            }
            for row in result
        ]
        return competitions

    def finalize_competition(self, competition_id: int) -> None:
        query = """
            select a.competition_competitor_id, count(*) votes from votes a
            inner join competition_competitors b on a.competition_competitor_id = b.id
            where b.competition_id = %s
            group by a.competition_competitor_id
            order by count(*) desc
            """
        result = self.execute_query(query, (competition_id,))

        total = 0
        for row in result:
            total += row[1]

        if len(result) > 0:
            max_vote_count = result[0][1]

        votes_summary = [
            {
                "competition_competitor_id": row[0],
                "vote_count": row[1],
                "vote_ratio": round(row[1] / total, 3),
                "is_winner": max_vote_count == row[1],
            }
            for row in result
        ]

        queries_params = []
        for vote in votes_summary:
            queries_params.append(
                (
                    "update competition_competitors set vote_count=%s, vote_ratio=%s, is_winner=%s where id = %s",
                    (
                        vote["vote_count"],
                        vote["vote_ratio"],
                        vote["is_winner"],
                        vote["competition_competitor_id"],
                    ),
                )
            )

        queries_params.append(
            (
                "UPDATE competitions SET status = 'published' WHERE id = %s AND status = 'ended'",
                (competition_id,),
            )
        )

        self.execute_transaction(queries_params)

    def latest_competition(self) -> Optional[Tuple[int, str]]:
        query = """
        SELECT id, name
        FROM competitions
        WHERE status = 'published' 
        ORDER BY voting_end_date DESC 
        LIMIT 1
        """

        result = self.execute_query(query)

        # Check if the result is not empty

        if result and len(result) > 0:
            return result[0][0], result[0][1]  # Unpack the first row (id, name)

        return None  # Return None if no result is found

    def champ_in_competition(self, competition_id: int) -> tuple:
        query = """
        SELECT competitors.name, competitors.image, competition_competitors.vote_count
        FROM competition_competitors 
        JOIN competitors ON competition_competitors.competitor_id = competitors.id
        WHERE competition_competitors.competition_id = %s
        ORDER BY competition_competitors.vote_count DESC 
        LIMIT 1
        """
        result = self.execute_query(query, (competition_id,))
        if result:
            return result[0][0], result[0][1], result[0][2]
        return None, None, None

    def get_competitions_by_theme_and_status(
        self, theme_id, status
    ) -> List[Competition]:
        query = """
            SELECT c.id, c.name, c.voting_start_date, c.voting_end_date, c.status, 
                comp.id, comp.name, comp.description, comp.image, comp.location
            FROM competitions c
            LEFT JOIN competition_competitors cc ON c.id = cc.competition_id
            LEFT JOIN competitors comp ON comp.id = cc.competitor_id
            WHERE c.theme_id = %s AND c.status = %s
            ORDER BY c.voting_start_date
        """
        result = self.execute_query(query, (theme_id, status))

        competitions = {}
        for row in result:
            competition_id = row[0]
            if competition_id not in competitions:
                competitions[competition_id] = Competition(
                    id=row[0],
                    name=row[1],
                    voting_start_date=row[2],
                    voting_end_date=row[3],
                    status=row[4],
                )
            competitor = Competitor(
                id=row[5],
                name=row[6],
                description=row[7],
                image=row[8],
                location=(
                    json.loads(row[9]) if row[9] else {}
                ),  # Handling location as JSON
            )
            competitions[competition_id].competitors.append(competitor)

        return list(competitions.values())

    def get_finalized_competition_results_by_theme(self, theme_id):
        query = """SELECT c.id AS competition_id, c.name AS competition_name, comp.name AS competitor_name,
                (SELECT SUM(cc2.vote_count) FROM competition_competitors cc2 
                WHERE cc2.competition_id = c.id) AS total_votes,CONCAT(ROUND((cc.vote_count / (SELECT SUM(cc2.vote_count) 
                FROM competition_competitors cc2 
                WHERE cc2.competition_id = c.id)) * 100, 1), '%') AS winner_votes_proportion
                FROM competition_competitors cc 
                JOIN competitions c ON cc.competition_id = c.id
                JOIN competitors comp ON cc.competitor_id = comp.id
                WHERE c.theme_id = %s AND c.status = 'published' AND cc.is_winner = 1
                ORDER BY c.voting_end_date DESC, c.name, cc.vote_count DESC;
                """

        return self.execute_query(query, (theme_id,))

    def get_competitor_votes(self, competition_id):
        query = """
            SELECT c.id, c.name, cc.vote_count 
            FROM competition_competitors cc
            JOIN competitors c ON cc.competitor_id = c.id
            WHERE cc.competition_id = %s
            ORDER BY cc.vote_count DESC
        """
        return self.execute_query(query, (competition_id,))
