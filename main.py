from fastapi import FastAPI, HTTPException
from typing import List
from http import HTTPStatus
from typing import Union
from pydantic import BaseModel
import os
# 6.  Cinema
#        Filme (id, título, gênero, duração, ano\lançamento, classificação)
#        Sessão (id, filme\id, sala, data\hora, preço\ingresso, lugares\disponíveis)
#        Ingresso (id, sessão\id, cliente\id, poltrona, data\compra, tipo)

app = FastAPI()
MOVIE_CSV_FILE = 'movies.csv'
SESSION_CSV_FILE = 'sessions.csv'
TICKET_CSV_FILE = 'tickets.csv'

#Filme (id, título, gênero, duração, ano\lançamento, classificação)
class Movie(BaseModel):
    id: int
    title: str
    genre: str
    duration: int  # in minutes
    release_year: int
    rating: str  # Livre, 10, 12, 14, 16 e 18 anos)

#Sessão (id, filme\id, sala, data\hora, preço\ingresso, lugares\disponíveis)
class Session(BaseModel):
    id: int
    movie: Movie
    room: str
    date_time: str  # ISO 8601 format (exemplo:  2020-07-10 15:00:00.000, representa 10 de julho de 2020 às 15:00:00)
    ticket_price: float
    available_seats: List #seria lugares disponiveis


#Ingresso (id, sessão\id, cliente\id, poltrona, data\compra, tipo)
class Ticket(BaseModel):
    id: int
    session: Session
    client_id: int
    seat: str # não sei como fica ainda, tem que ver a questão do available_seats mas se for string seria tipo F8
    purchase_date: str #msm formato do date_time
    ticket_type: str # Normal, meia-entrada, promocional


def read_movies_csv()->List[Movie]:
    movies: List[Movie] = []
    if os.path.exists(MOVIE_CSV_FILE):
        with open(MOVIE_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None) #ignora o header
            for line in file:
                id, title, genre, duration, release_year, rating = line.strip().split(',')
                movies.append(
                    Movie(
                        id=int(id),
                        title=title, 
                        genre=genre, 
                        duration=int(duration), 
                        release_year=int(release_year), 
                        rating=rating
                        )
                    )
    return movies

def write_movies_csv(movies):
    with open(MOVIE_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,title,genre,duration,release_year,rating\n")
        for movie in movies:
            file.write(f"{movie.id},{movie.title},{movie.genre},{movie.duration},{movie.release_year},{movie.rating}\n")

@app.get("/movies", response_model=List[Movie])
def get_movies():
    movies = read_movies_csv()
    return movies

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie_by_id(movie_id: int):
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id:
            return movie
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found") 

@app.post("/movies", response_model=Movie, status_code=HTTPStatus.CREATED)
def create_movie(movie: Movie):
    movies = read_movies_csv()
    if any(m.id == movie.id for m in movies):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Movie with this ID already exists")
    movies.append(movie)
    write_movies_csv(movies)
    return movie

@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, updated_movie: Movie):
    movies = read_movies_csv()
    for index, movie in enumerate(movies):
        if movie.id == movie_id:
            movies[index] = updated_movie
            write_movies_csv(movies)
            return updated_movie
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@app.delete("/movies/{movie_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_movie(movie_id: int):
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id:
            movies.remove(movie)
            write_movies_csv(movies)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")


#estrura para verificar rating(validar)
#deixar id gerando automaticamente
#validar se o filme existe antes de criar a sessão
#validar se o filme deletado existe na sessão