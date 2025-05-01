from fastapi import FastAPI, HTTPException
from typing import List
from http import HTTPStatus
from pydantic import BaseModel
import os
# 6.  Cinema
#        Filme (id, título, gênero, duração, ano\lançamento, classificação)
#        Sessão (id, filme\id, sala, data\hora, preço\ingresso, lugares\disponíveis)
#        Ingresso (id, sessão\id, cliente\id, poltrona, data\compra, tipo)

app = FastAPI()
SESSION_CSV_FILE = "session.csv"

typing_str_list = List[str]

class Session(BaseModel):
    SessionID: int
    Movie: str
    Room: str
    DateTime: str 
    TicketPrice: float
    AvailableSeats: typing_str_list

# Utility functions

def read_session_csv() -> List[Session]:
    sessions: List[Session] = []
    if os.path.exists(SESSION_CSV_FILE):
        with open(SESSION_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None) #ignora o header
            for line in file:
                SessionID,Movie,Room,DateTime,TicketPrice,AvailableSeats = line.strip().split(',')
                sessions.append(
                    Session(
                        SessionID=int(SessionID),
                        Movie=Movie, 
                        Room=Room, 
                        DateTime=DateTime, 
                        TicketPrice=float(TicketPrice), 
                        AvailableSeats=AvailableSeats.split(';')
                    )
                )
    return sessions


def write_session_csv(sessions):
    with open(SESSION_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("SessionID,Movie,Room,DateTime,TicketPrice,AvailableSeats\n")
        for session in sessions:
            file.write(f"{session.SessionID},{session.Movie},{session.Room},{session.DateTime},{session.TicketPrice},{';'.join(session.AvailableSeats)}\n")
            # AvailableSeats é uma lista de strings, então usamos join para convertê-la em uma string separada por ponto e vírgula

# CRUD Endpoints

@app.get("/sessions", response_model=List[Session])
def get_sessions():
    sessions = read_session_csv()
    return sessions

@app.get("/sessions/{session_id}", response_model=Session)
def get_session_by_id(session_id: int):
    sessions = read_session_csv()
    for session in sessions:
        if session.SessionID == session_id:
            return session
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@app.post("/sessions", response_model=Session, status_code=HTTPStatus.CREATED)
def create_session(session: Session):
    sessions = read_session_csv()
    if any(s.SessionID == session.SessionID for s in sessions):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Session with this ID already exists")
    sessions.append(session)
    write_session_csv(sessions)
    return session

@app.put("/sessions/{session_id}", response_model=Session)
def update_session(session_id: int, updated_session: Session):
    sessions = read_session_csv()
    for index, session in enumerate(sessions):
        if session.SessionID == session_id:
            sessions[index] = updated_session
            if updated_session.SessionID != session_id:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            write_session_csv(sessions)
            return updated_session
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@app.delete("/sessions/{session_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_session(session_id: int):
    sessions = read_session_csv()
    for session in sessions:
        if session.SessionID == session_id:
            sessions.remove(session)
            write_session_csv(sessions)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

#estrura para verificar rating(validar)
#deixar id gerando automaticamente
#validar se o filme existe antes de criar a sessão
#validar se o filme deletado existe na sessão