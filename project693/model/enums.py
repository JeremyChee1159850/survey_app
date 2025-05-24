from enum import Enum


class Role(Enum):
    SITEADMIN = "siteadmin"

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"