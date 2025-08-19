from dataclasses import dataclass
from datetime import datetime
from typing import List
from enum import Enum, auto

class Intent(Enum):
    GREETING = auto()
    FAREWELL = auto()
    NAME_SET = auto()
    NAME_GET = auto()
    NAME_CHANGE = auto()
    HELP = auto()
    CONFIRM = auto()
    DENY = auto()
    UNKNOWN = auto()

    # Movie booking intents
    MOVIE_SEARCH = auto()
    MOVIE_SELECT = auto()
    SHOW_TIME_SELECT = auto()
    SEAT_SELECT = auto()
    BOOKING_CONFIRM = auto()
    BOOKING_CANCEL = auto()
    BOOKING_STATUS = auto()

@dataclass
class Movie:
    id: str
    title: str
    duration: int  # in minutes
    language: str
    genre: str

@dataclass
class ShowTime:
    id: str
    movie_id: str
    datetime: datetime
    available_seats: List[str]
    price: float

@dataclass
class Booking:
    id: str
    user_name: str
    movie_id: str
    showtime_id: str
    seats: List[str]
    total_amount: float
    status: str
    timestamp: datetime

@dataclass
class ConversationTurn:
    timestamp: float
    user_input: str
    response: str
    intent: Intent