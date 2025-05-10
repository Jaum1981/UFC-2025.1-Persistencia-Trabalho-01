import os
import zipfile
import yaml
import logging.config
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse
from http import HTTPStatus
from models.models import Movie
from typing import List

# Configuração de logging antes de instanciar o logger

def movie_setup_logging(
        default_path: str = './logs/configMovie.yaml',
        default_level: int = logging.INFO,
        env_key: str = 'LOG_CFG'
) -> None:
    """
    Carrega configurações de logging de um arquivo YAML
    e aplica-as via logging.config.dictConfig().
    Cria diretório de logs se necessário.
    """
    # Garante que o diretório exista
    config_dir = os.path.dirname(default_path) or '.'
    os.makedirs(config_dir, exist_ok=True)

    # Sobrescreve via variável de ambiente
    path = os.getenv(env_key, default_path)

    if os.path.exists(path):
        with open(path, 'rt', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    else:
        # Configuração básica caso não encontre o arquivo
        logging.basicConfig(level=default_level,
                            format="%(asctime)s - %(levelname)s - %(message)s",
                            handlers=[logging.FileHandler('movie.log', encoding='utf-8')])

# Executa setup ao importar este módulo
movie_setup_logging()
# Instancia o logger após configuração
movie_logger = logging.getLogger("movie_logger")

router = APIRouter()
MOVIE_CSV_FILE = 'data/movies.csv'
MOVIE_ZIP_FILE = 'data/movies.zip'

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
    movie_logger.info("Fetching all movies")
    movies = read_movies_csv()
    movie_logger.debug(f"{len(movies)} movies found")
    return movies

@router.get("/movies/{movie_id}", response_model=Movie)
def get_movie_by_id(movie_id: int):
    movie_logger.info(f"Fetching movie with ID: {movie_id}")
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id:
            movie_logger.debug(f"Movie found: {movie.title}")
            return movie
    movie_logger.error(f"Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found") 

@router.post("/movies", response_model=Movie, status_code=HTTPStatus.CREATED)
def create_movie(movie: Movie):
    movie_logger.info(f"Creating movie: {movie.title}")
    movies = read_movies_csv()
    if any(m.id == movie.id for m in movies):
        movie_logger.error(f"Movie with ID {movie.id} already exists")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Movie with this ID already exists")
    movies.append(movie)
    write_movies_csv(movies)
    movie_logger.debug(f"Movie created: {movie.title}")
    return movie

@router.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, updated_movie: Movie):
    movie_logger.info(f"Updating movie with ID: {movie_id}")
    movies = read_movies_csv()
    for index, movie in enumerate(movies):
        if movie.id == movie_id:
            movies[index] = updated_movie
            movie_logger.debug(f"Movie updated: {updated_movie.title}")
            if updated_movie.id != movie_id:
                movie_logger.error("Cannot change movie ID")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change movie ID")
            write_movies_csv(movies)
            return updated_movie
    movie_logger.error(f"Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.delete("/movies/{movie_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_movie(movie_id: int):
    movie_logger.info(f"Deleting movie with ID: {movie_id}")
    movies = read_movies_csv()
    for movie in movies:
        if movie.id == movie_id: 
            movies.remove(movie)
            write_movies_csv(movies)
            movie_logger.debug(f"Movie deleted: {movie.title}")
            return
    movie_logger.error(f"Movie with ID {movie_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Movie not found")

@router.get("/movies-count")
def get_movies_count():
    movie_logger.info("Counting all movies")
    movies = read_movies_csv()
    return  {
        "quantidade": len(movies)
    }

@router.get("/movies-zip")
def get_movies_zip():
    movie_logger.info("Creating ZIP file of movies")
    with zipfile.ZipFile(MOVIE_ZIP_FILE, 'w') as zipf:
        zipf.write(MOVIE_CSV_FILE, os.path.basename(MOVIE_CSV_FILE))
        movie_logger.debug(f"ZIP file created: {MOVIE_ZIP_FILE}")
        return FileResponse(MOVIE_ZIP_FILE, media_type='application/zip', filename=os.path.basename(MOVIE_ZIP_FILE))
    
@router.get("/movies-per-atributes", response_model=List[Movie])
def get_movies_by_atribute(field: str = Query(..., description="Coluna para busca (e.g. id, title, genre)"),
                           value: str = Query(..., description="Valor a ser buscado na coluna")):
    movie_logger.info(f"Fetching movies by attribute: {field} with value: {value}")
    movies = read_movies_csv()
    if field not in Movie.__annotations__:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid field")
    
    if field == "id":
        value = int(value)
    elif field == "duration_minutes":
        value = int(value)
    elif field == "release_year":
        value = int(value)
    else:
        value = str(value)  
    filtered_movies = []
    for movie in movies:
        movie_value = getattr(movie, field)
        if field == "genre":
            if value in movie_value.split(';'):
                filtered_movies.append(movie)
        else:
            if movie_value == value:
                filtered_movies.append(movie)
    
    if not filtered_movies:
        movie_logger.error(f"No movies found with {field} = {value}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No movies found with the given attribute")
    movie_logger.debug(f"{len(filtered_movies)} movies found with {field} = {value}")
    return filtered_movies

#F6 Retornar o Hash SHA256 do Arquivo CSV
@router.get("/movies-hash")
def get_movies_hash():
    movie_logger.info("Calculating SHA256 hash of the movies CSV file")
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(MOVIE_CSV_FILE, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return {
        "hash": sha256_hash.hexdigest()
    }
