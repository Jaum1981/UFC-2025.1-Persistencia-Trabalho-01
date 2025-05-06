import os
import zipfile
from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse
from http import HTTPStatus
from models.models import Movie
from typing import List

router = APIRouter()
MOVIE_CSV_FILE = 'data/movies.csv'
ZIP_FILE = 'data/movies.zip'

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

def write_movies_csv(movies: List[Movie]) -> None:
    with open(MOVIE_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,title,genre,director,duration_minutes,release_year,rating\n")
        for movie in movies:
            file.write(f"{movie.id},{movie.title},{movie.genre},{movie.director},{movie.duration_minutes},{movie.release_year},{movie.rating}\n")


@router.get("/movies", response_model=List[Movie])
def get_movies():
    movies = read_movies_csv()
    return movies

@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie_by_id(movie_id: int):
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id:
            return movie
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found") 

@router.post("/movies", response_model=Movie, status_code=HTTPStatus.CREATED)
def create_movie(movie: Movie):
    movies = read_movies_csv()
    if any(m.id == movie.id for m in movies):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Movie with this ID already exists")
    movies.append(movie)
    write_movies_csv(movies)
    return movie

@router.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, updated_movie: Movie):
    movies = read_movies_csv()
    for index, movie in enumerate(movies):
        if movie.id == movie_id:
            movies[index] = updated_movie
            if updated_movie.id != movie_id:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change movie ID")
            write_movies_csv(movies)
            return updated_movie
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.delete("/movies/{movie_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_movie(movie_id: int):
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id: 
            movies.remove(movie)
            write_movies_csv(movies)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.get("/movies-count", response_model=int)
def get_movies_count():
    movies = read_movies_csv()
    return len(movies)

@router.get("/movies-zip")
def get_movies_zip():
    with zipfile.ZipFile(ZIP_FILE, 'w') as zipf:
        zipf.write(MOVIE_CSV_FILE, os.path.basename(MOVIE_CSV_FILE))
        return FileResponse(ZIP_FILE, media_type='application/zip', filename=os.path.basename(ZIP_FILE))