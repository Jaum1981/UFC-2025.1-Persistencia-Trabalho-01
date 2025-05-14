import os
import zipfile
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse
from http import HTTPStatus
from models.models import Movie
from typing import List, Optional
from utils.logger_config import logger
from utils.configs import ler_config_yaml

router = APIRouter()
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

def write_movies_csv(movies: List[Movie]) -> None:
    with open(MOVIE_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,title,genre,director,duration_minutes,release_year,rating\n")
        for movie in movies:
            file.write(f"{movie.id},{movie.title},{movie.genre},{movie.director},{movie.duration_minutes},{movie.release_year},{movie.rating}\n")


@router.get("/movies", response_model=List[Movie])
def get_movies():
    logger.info("[get_movies] - Fetching all movies.")
    movies = read_movies_csv()
    logger.debug(f"[get_movies] - {len(movies)} movies found.")
    logger.info("[get_movies] - Movies recovered successfully.")
    return movies

@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie_by_id(movie_id: int):
    logger.info(f"[get_movie_by_id] - Fetching movie with ID: {movie_id}")
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id:
            logger.info(f"[get_movie_by_id] - Movie found: {movie.title}")
            return movie
    logger.error(f"[get_movie_by_id] - Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found") 

@router.post("/movies", response_model=Movie, status_code=HTTPStatus.CREATED)
def create_movie(movie: Movie):
    logger.info(f"[create_movie] - Creating movie: {movie.title}")
    movies = read_movies_csv()
    if any(m.id == movie.id for m in movies):
        logger.error(f"[create_movie] - Movie with ID {movie.id} already exists")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Movie with this ID already exists")
    movies.append(movie)
    write_movies_csv(movies)
    logger.info(f"[create_movie] - Movie created: {movie.title}")
    return movie

@router.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, updated_movie: Movie):
    logger.info(f"[update_movie] - Updating movie with ID: {movie_id}")
    movies = read_movies_csv()
    for index, movie in enumerate(movies):
        if movie.id == movie_id:
            movies[index] = updated_movie
            logger.info(f"[update_movie] - Movie updated: {updated_movie.title}")
            if updated_movie.id != movie_id:
                logger.error("[update_movie] - Cannot change movie ID")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change movie ID")
            write_movies_csv(movies)
            return updated_movie
    logger.error(f"[update_movie] - Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.delete("/movies/{movie_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_movie(movie_id: int):
    logger.info(f"[delete_movie] - Deleting movie with ID: {movie_id}")
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id: 
            movies.remove(movie)
            write_movies_csv(movies)
            logger.info(f"[delete_movie] - Movie deleted: {movie.title}")
            return
    logger.error(f"[delete_movie] - Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.get("/movies-count")
def get_movies_count():
    logger.info("[get_movies_count] - Counting all movies")
    movies = read_movies_csv()
    return  {
        "quantidade": len(movies)
    }

@router.get("/movies-zip")
def get_movies_zip():
    logger.info("[get_movies_zip] - Creating ZIP file of movies")
    with zipfile.ZipFile(MOVIE_ZIP_FILE, 'w') as zipf:
        zipf.write(MOVIE_CSV_FILE, os.path.basename(MOVIE_CSV_FILE))
        logger.info(f"[get_movies_zip] - ZIP file created: {MOVIE_ZIP_FILE}")
        return FileResponse(MOVIE_ZIP_FILE, media_type='application/zip', filename=os.path.basename(MOVIE_ZIP_FILE))
    
@router.get("/movies-filter", response_model=List[Movie])
def filter_movies(
    genre: Optional[str] = Query(None, description="Gênero do filme"),
    director: Optional[str] = Query(None, description="Nome do diretor"),
    min_duration: Optional[int] = Query(None, description="Duração mínima em minutos"),
    max_duration: Optional[int] = Query(None, description="Duração máxima em minutos"),
    release_year: Optional[int] = Query(None, description="Ano de lançamento exato"),
    title: Optional[str] = Query(None, description="Título ou parte do título")
):
    logger.info("[filter_movies] - Starting search with movie filtering.")
    logger.debug("[filter_movies] - Filtering attributes:")
    logger.debug(f"[filter_movies] - genre: {genre}")
    logger.debug(f"[filter_movies] - director: {director}")
    logger.debug(f"[filter_movies] - min_duration: {min_duration}")
    logger.debug(f"[filter_movies] - max_duration: {max_duration}")
    logger.debug(f"[filter_movies] - release_year: {release_year}")
    logger.debug(f"[filter_movies] - title: {title}")
    movies = read_movies_csv()
    results: List[Movie] = []
    for movie in movies:
        if genre is not None and genre.lower() not in [g.lower() for g in movie.genre.split(';')]:
            continue
        if director is not None and director.lower() not in movie.director.lower():
            continue
        if min_duration is not None and movie.duration_minutes < min_duration:
            continue
        if max_duration is not None and movie.duration_minutes > max_duration:
            continue
        if release_year is not None and movie.release_year != release_year:
            continue
        if title is not None and title.lower() not in movie.title.lower():
            continue
        results.append(movie)
    return results

#F6 Retornar o Hash SHA256 do Arquivo CSV
@router.get("/movies-hash")
def get_movies_hash():
    logger.info("[get_movies_hash] - Calculating SHA256 hash of the movies CSV file.")
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(MOVIE_CSV_FILE, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return {
        "hash_sha256": sha256_hash.hexdigest()
    }

#F8 Converter o csv para xml
@router.get("/movies-xml")
def get_movies_xml():
    logger.info("[get_movies_xml] - Converting movies CSV to XML")
    import xml.etree.ElementTree as ET
    movies = read_movies_csv()
    root = ET.Element("movies")
    for movie in movies:
        movie_elem = ET.SubElement(root, "movie")
        for key, value in movie.dict().items():
            child = ET.SubElement(movie_elem, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    xml_file_path = movies_data.get('xml', {}).get('movies', 'xml_files/movies.xml')
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    return FileResponse(xml_file_path, media_type='application/xml', filename=os.path.basename(xml_file_path))