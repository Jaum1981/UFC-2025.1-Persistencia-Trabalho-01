import os
import datetime
from utils.configs import ler_config_yaml
from models.models import Movie, Ticket, Session
from typing import List

movies_data = ler_config_yaml().get('data', {})
MOVIE_CSV_FILE = movies_data.get('csv', {}).get('movies', 'data/movies.csv')
MOVIE_ZIP_FILE = movies_data.get('compressed', {}).get('movies', 'compressed/movies.zip')

def read_movies_csv() -> List[Movie]:
    movies: List[Movie] = []
    if os.path.exists(MOVIE_CSV_FILE):
        with open(MOVIE_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None) #ignora o header
            for line in file:
                id, title, genre, director, duration_minutes, release_year, rating = line.strip().split(',')
                movies.append(
                    Movie(
                        id=int(id),
                        title=title, 
                        genre=genre,
                        director=director,
                        duration_minutes=int(duration_minutes), 
                        release_year=int(release_year), 
                        rating=rating
                        )
                    )
    return movies


TICKET_CSV_FILE = movies_data.get('csv', {}).get('ticket', 'data/ticket.csv')
TICKET_ZIP_FILE = movies_data.get('compressed', {}).get('ticket', 'compressed/ticket.zip')

# Utility functions

def read_tickets_csv() -> List[Ticket]:
    tickets: List[Ticket] = []
    if os.path.exists(TICKET_CSV_FILE):
        with open(TICKET_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None)  # ignora o header
            for line in file:
                id, session_id, client_name, seat, purchase_date, ticket_type, price = line.strip().split(',')
                tickets.append(
                    Ticket(
                        id=int(id),
                        session_id=int(session_id),
                        client_name=client_name,
                        seat=seat,
                        purchase_date=datetime.fromisoformat(purchase_date),
                        ticket_type=ticket_type,
                        price=price
                    )
                )
    return tickets


SESSION_CSV_FILE = movies_data.get('csv', {}).get('session', 'data/session.csv')
SESSION_ZIP_FILE = movies_data.get('compressed', {}).get('session', 'compressed/session.zip')

def read_session_csv() -> List[Session]:
    sessions: List[Session] = []
    if os.path.exists(SESSION_CSV_FILE):
        with open(SESSION_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None) #ignora o header
            for line in file:
                id, movie_id, start_time, room, available_seats = line.strip().split(',')
                sessions.append(
                    Session(
                        id=int(id),
                        movie_id=movie_id, 
                        start_time=datetime.fromisoformat(start_time), 
                        room=room, 
                        available_seats=available_seats.split(';')
                    )
                )
    return sessions
