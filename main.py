from fastapi import FastAPI
from routers import movie, session, ticket
from routers.movie import movie_setup_logging
from routers.session import session_setup_logging


movie_setup_logging()
session_setup_logging()
app = FastAPI()

# Importando os routers
app.include_router(movie.router, tags=["Movies"])
app.include_router(session.router, tags=["Sessions"])
app.include_router(ticket.router, tags=["Tickets"])