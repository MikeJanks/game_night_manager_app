from enum import Enum


class EventStatus(str, Enum):
    PLANNING = "PLANNING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class MembershipRole(str, Enum):
    HOST = "HOST"
    ATTENDEE = "ATTENDEE"


class MembershipStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"


class ExternalSource(str, Enum):
    DISCORD = "discord"
