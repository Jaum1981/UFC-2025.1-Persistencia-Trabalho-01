from fastapi import FastAPI
from routers import movie, session, ticket

app = FastAPI()

# Importando os routers
app.include_router(movie.router, tags=["Movies"])
app.include_router(session.router, tags=["Sessions"])
app.include_router(ticket.router, tags=["Tickets"])