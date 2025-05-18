from project693.dao.base_dao import BaseDAO
from project693.model.competitor import Competitor
from typing import List
import json
import random # this is for project693


class CompetitorDAO(BaseDAO):

    def __init__(self) -> None:
        super().__init__()

    def add_plant(self, name: str, description: str, image: str, location: str, invasiveness: str) -> None:
        query = """
            INSERT INTO plants (name, description, image, location, invasiveness)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.execute_non_query(query, (name, description, image, location, invasiveness))

    def edit_plant(self, id: int, name: str, description: str, image: str, location: str) -> None:
        query = """
            UPDATE plants
            SET name = %s, description = %s, image = %s, location = %s
            WHERE id = %s
        """
        self.execute_non_query(query, (name, description, image, location, id))


    def delete_plant(self, id: int) -> None:
        query = "DELETE FROM plants WHERE id = %s"
        self.execute_non_query(query, (id,))

    def search_plants(self, keyword: str) -> List[Competitor]:
        query = """
            SELECT id, name, description, image, location, invasiveness
            FROM plants
            WHERE name LIKE %s OR description LIKE %s
        """
        result = self.execute_query(query, (f"%{keyword}%", f"%{keyword}%"))
        
        plants = []
        for row in result:
            plant = Competitor(
                id=row[0], 
                name=row[1], 
                description=row[2], 
                image=row[3],
                location=json.loads(row[4]) if row[4] else {},  # Handle NULL or empty location
                invasiveness=row[5]
            )
            plants.append(plant)
        
        return plants

    def get_plant_by_id(self, id: int) -> Competitor:
        query = "SELECT * FROM plants WHERE id = %s"
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
    
    # project693
    def get_all_plants(self) -> List[Competitor]:
        query = "SELECT id, name, description, image, location, invasiveness FROM plants"
        result = self.execute_query(query)

        plants = []
        for row in result:
            plant = Competitor(
                id=row[0],
                name=row[1],
                description=row[2],
                image=row[3],
                location=json.loads(row[4]) if row[4] else {},
                invasiveness=row[5]
            )
            plants.append(plant)
        
        return plants
    

    # project693
    def get_random_pair(self, used_invasive_ids=None, used_non_invasive_ids=None) -> List[Competitor]:
        all_plants = self.get_all_plants()

        # Separate the plants
        invasive = [c for c in all_plants if c.invasiveness == 'invasive']
        non_invasive = [c for c in all_plants if c.invasiveness == 'non-invasive']

        # Filter out already used plants
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
    def survey_answer(self, session_id, question_number, selected_plant_id):
        query = """
                INSERT INTO survey_results (session_id, question_number, selected_plant_id)
                VALUES (%s, %s, %s)
                """
        self.execute_non_query(query, (session_id, question_number, selected_plant_id))

    # Save the Introduction Questions
    def save_metadata(self, session_id, has_garden=None, age=None, reasoning=None):
        query = """
                INSERT INTO survey_metadata (session_id, has_garden, age, reasoning)
                VALUES (%s, %s, %s, %s)
                """
        self.execute_non_query(query, (session_id, has_garden, age, reasoning))

    # Update Q10 which is the Reasoning Question
    def update_reasoning(self, session_id, reasoning):
        query = """
                UPDATE survey_metadata SET reasoning = %s WHERE session_id = %s
                """
        self.execute_non_query(query, (reasoning, session_id))