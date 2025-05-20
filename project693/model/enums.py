from enum import Enum


class Role(Enum):
    VOTER = "voter"
    SITEADMIN = "siteadmin"


class CompetitionRole(Enum):
    SCRUTINEER = "scrutineer"
    ADMIN = "admin"


class CommunityRole(Enum):
    MODERATOR = "moderator"


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class CompetitionStatus(Enum):
    PENDING = "pending"
    ONGOING = "ongoing"
    ENDED = "ended"
    PUBLISHED = "published"


class VoteStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"


class VotingPermission(Enum):
    ALLOWED = "allowed"
    BANNED = "banned"


class ApplicationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DonationStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class ReceiptStatus(Enum):
    PENDING = "pending"
    GENERATED = "generated"
    SENT = "sent"