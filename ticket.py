from fastapi import FastAPI, HTTPException
from typing import List
from http import HTTPStatus
from pydantic import BaseModel
from session import Session
import os
# 6.  Cinema
#        Filme (id, título, gênero, duração, ano\lançamento, classificação)
#        Sessão (id, filme\id, sala, data\hora, preço\ingresso, lugares\disponíveis)
#        Ingresso (id, sessão\id, cliente\id, poltrona, data\compra, tipo)

app = FastAPI()
MOVIE_CSV_FILE = 'movies.csv'
SESSION_CSV_FILE = 'sessions.csv'
TICKET_CSV_FILE = 'tickets.csv'


#Ingresso (id, sessão\id, cliente\id, poltrona, data\compra, tipo)
class Ticket(BaseModel):
    id: int
    session: Session
    client_id: int
    seat: str # não sei como fica ainda, tem que ver a questão do available_seats mas se for string seria tipo F8
    purchase_date: str #msm formato do date_time
    ticket_type: str # Normal, meia-entrada, promocional
