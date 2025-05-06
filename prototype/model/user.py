from prototype.model.enums import (
    Role,
    Status,
    VotingPermission,
    CompetitionRole,
    CommunityRole,
)


class User:
    def __init__(
        self,
        id,
        username,
        password_hash,
        email,
        first_name,
        last_name,
        location,
        description,
        avatar,
        role,
        status,
        voting_permission,
        theme_role_mapping,
        community_role_mapping,
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.location = location
        self.description = description
        self.avatar = avatar
        self.theme_role_mapping = theme_role_mapping
        self.community_role_mapping = community_role_mapping

        # Pass enum directly without calling upper()
        if isinstance(role, Role):
            self.role = role
        else:
            raise ValueError(f"Invalid role: {role}")

        if isinstance(status, Status):
            self.status = status
        else:
            raise ValueError(f"Invalid status: {status}")

        if isinstance(voting_permission, VotingPermission):
            self.voting_permission = voting_permission
        else:
            raise ValueError(f"Invalid voting permission: {voting_permission}")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "location": self.location,
            "description": self.description,
            "avatar": self.avatar,
            "role": self.role.value,
            "status": self.status.value,
            "voting_permission": self.voting_permission.value,
            "theme_role_mapping": (
                {
                    int(theme_id): role.value
                    for theme_id, role in self.theme_role_mapping.items()
                }
                if self.theme_role_mapping
                else None
            ),
            "community_role_mapping": (
                {
                    int(theme_id): role.value
                    for theme_id, role in self.community_role_mapping.items()
                }
                if self.community_role_mapping
                else None
            ),
        }

    @staticmethod
    def from_dict(data):
        return User(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            location=data["location"],
            description=data["description"],
            avatar=data["avatar"],
            role=Role[data["role"].upper()],  # Convert string to Role enum
            status=Status[data["status"].upper()],  # Convert string to Status enum
            voting_permission=VotingPermission[
                data["voting_permission"].upper()
            ],  # Convert string to VotingPermission enum
            theme_role_mapping=(
                {
                    int(theme_id): CompetitionRole[role.upper()]
                    for theme_id, role in data.get("theme_role_mapping", {}).items()
                }
                if data.get("theme_role_mapping")
                else None
            ),
            community_role_mapping=(
                {
                    int(theme_id): CommunityRole[role.upper()]
                    for theme_id, role in data.get("community_role_mapping", {}).items()
                }
                if data.get("community_role_mapping")
                else None
            ),
        )
