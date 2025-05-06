class Theme:
    def __init__(self, id, name, description, application_id):
        self.id = id
        self.name = name
        self.description = description
        self.application_id = application_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "application_id": self.application_id,
        }
