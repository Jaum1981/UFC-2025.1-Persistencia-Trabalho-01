from typing import List
from pydantic import BaseModel
from datetime import datetime

class Movie(BaseModel):
    id: int
    title: str
    genre: str
    director: str
    duration_minutes: int
    release_year: int
    rating: str  # (Livre, 10, 12, 14, 16 e 18 anos)

class Session(BaseModel):
    id: int
    movie_id: str
    start_time: datetime
    room: str
    available_seats: List[str]

class Ticket(BaseModel):
    id: int
    session_id: int
    client_name: str
    seat: str
    purchase_date: datetime
    ticket_type: str # Normal, meia-entrada, promocional
    price: float