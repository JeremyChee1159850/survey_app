from project693.model.enums import VoteStatus

class Vote:
    def __init__(
        self,
        competition_competitor_id,
        voter_id,
        voting_time,
        voting_ip,
        status,
        id=None,
    ):
        self.id = id
        self.competition_competitor_id = competition_competitor_id
        self.voter_id = voter_id
        self.voting_time = voting_time
        self.voting_ip = voting_ip

        if isinstance(status, VoteStatus):
            self.status = status
        else:
            try:
                self.status = VoteStatus[status.upper()]
            except KeyError:
                raise ValueError(f"Invalid status: {status}")

    def to_dict(self):
        return {
            "id": self.id,
            "competition_competitor_id": self.competition_competitor_id,
            "voter_id": self.voter_id,
            "voting_time": self.voting_time,
            "voting_ip": self.voting_ip,
            "status": self.status.value,
        }

    @staticmethod
    def from_dict(data):
        return Vote(
            id=data.get("id"),
            competition_competitor_id=data["competition_competitor_id"],
            voter_id=data["voter_id"],
            voting_time=data["voting_time"],
            voting_ip=data["voting_ip"],
            status=data["status"],
        )

