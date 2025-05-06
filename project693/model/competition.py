from project693.model.enums import CompetitionStatus
from project693.model.competitor import Competitor

class Competition:
    def __init__(
        self,
        id,
        name,
        voting_start_date,
        voting_end_date,
        status,
    ):

        self.id = id
        self.name = name
        self.voting_start_date = voting_start_date
        self.voting_end_date = voting_end_date
        self.status = status

        self.competitors = []

        if isinstance(status, CompetitionStatus):
            self.status = status
        else:
            try:
                self.status = CompetitionStatus[status.upper()]
            except KeyError:
                raise ValueError(f"Invalid status: {status}")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "voting_start_date": self.voting_start_date,
            "voting_end_date": self.voting_end_date,
            "status": self.status.value,
            "competitors": [competitor.to_dict() for competitor in self.competitors]
        }

    @staticmethod
    def from_dict(data):
        competition = Competition(
            id=data["id"],
            name=data["name"],
            voting_start_date=data["voting_start_date"],
            voting_end_date=data["voting_end_date"],
            status=data["status"],
        )
        competition.competitors = [Competitor.from_dict(comp) for comp in data.get("competitors", [])]
        return competition
    
class CompetitionResult:
    def __init__(self, competition_id, competition_name, competition_winner, total_votes, winner_votes_proportion):
        self.competition_id = competition_id
        self.competition_name = competition_name
        self.competition_winner = competition_winner
        self.total_votes = total_votes
        self.winner_votes_proportion = winner_votes_proportion

