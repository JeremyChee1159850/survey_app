from project693.dao.base_dao import BaseDAO
from project693.model.competitor import Competitor
from typing import List
import json
import random # this is for prototype


class CompetitorDAO(BaseDAO):

    def __init__(self) -> None:
        super().__init__()

    def add_competitor(self, name: str, description: str, image: str, location: str, invasiveness: str) -> None:
        query = """
            INSERT INTO competitors (name, description, image, location, invasiveness)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_non_query(query, (name, description, image, location, invasiveness))

    def edit_competitor(self, id: int, name: str, description: str, image: str, location: str) -> None:
        query = """
            UPDATE competitors
            SET name = %s, description = %s, image = %s, location = %s
            WHERE id = %s
        """
        self.execute_non_query(query, (name, description, image, location, id))


    def delete_competitor(self, id: int) -> None:
        query = "DELETE FROM competitors WHERE id = %s"
        self.execute_non_query(query, (id,))

    def search_competitor(self, keyword: str) -> List[Competitor]:
        query = """
            SELECT id, name, description, image, location, invasiveness
            FROM competitors
            WHERE name LIKE %s OR description LIKE %s
        """
        result = self.execute_query(query, (f"%{keyword}%", f"%{keyword}%"))
        
        competitors = []
        for row in result:
            competitor = Competitor(
                id=row[0], 
                name=row[1], 
                description=row[2], 
                image=row[3],
                location=json.loads(row[4]) if row[4] else {},  # Handle NULL or empty location
                invasiveness=row[5]
            )
            competitors.append(competitor)
        
        return competitors

    def get_competitor_by_id(self, id: int) -> Competitor:
        query = "SELECT * FROM competitors WHERE id = %s"
        result = self.execute_query(query, (id,))
        if result:
            row = result[0]
            return Competitor(
                id=row[0],
                name=row[1],
                description=row[2],
                image=row[3],
                location=json.loads(row[4]),
                invasiveness=row[5]
            )
        return None
    
    # prototype
    def get_all_competitors(self) -> List[Competitor]:
        query = "SELECT id, name, description, image, location, invasiveness FROM competitors"
        result = self.execute_query(query)

        competitors = []
        for row in result:
            competitor = Competitor(
                id=row[0],
                name=row[1],
                description=row[2],
                image=row[3],
                location=json.loads(row[4]) if row[4] else {},
                invasiveness=row[5]
            )
            competitors.append(competitor)
        
        return competitors
    

    # prototype
    def get_random_pair(self, used_invasive_ids=None, used_non_invasive_ids=None) -> List[Competitor]:
        all_competitors = self.get_all_competitors()

        # Separate the competitors
        invasive = [c for c in all_competitors if c.invasiveness == 'invasive']
        non_invasive = [c for c in all_competitors if c.invasiveness == 'non-invasive']

        # Filter out already used competitors
        if used_invasive_ids:
            invasive = [c for c in invasive if c.id not in used_invasive_ids]
        if used_non_invasive_ids:
            non_invasive = [c for c in non_invasive if c.id not in used_non_invasive_ids]

        # If none left, return empty
        if not invasive or not non_invasive:
            return []

        # Pick one of each and shuffle
        return random.sample([
            random.choice(invasive),
            random.choice(non_invasive)
        ], 2)
    
    # Answers of survey that get stored in the database
    def survey_answer(self, user_id, question_number, selected_competitor_id, reasoning=None):
        query = """
                INSERT INTO survey_results (user_id, question_number, selected_competitor_id, reasoning)
                VALUES (%s, %s, %s, %s)
                """
        self.execute_non_query(query, (user_id, question_number, selected_competitor_id, reasoning))