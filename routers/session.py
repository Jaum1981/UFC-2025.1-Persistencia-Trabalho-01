import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from models.models import Session
from typing import List

router = APIRouter()
SESSION_CSV_FILE = 'data/session.csv'

# Utility functions

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


def write_session_csv(sessions):
    with open(SESSION_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,movie_id,start_time,room,available_seats\n")
        for session in sessions:
            file.write(f"{session.id},{session.movie_id},{session.start_time.isoformat()},{session.room},{';'.join(session.available_seats)}\n")
            # AvailableSeats é uma lista de strings, então usamos join para convertê-la em uma string separada por ponto e vírgula

# CRUD Endpoints

@router.get("/sessions", response_model=List[Session])
def get_sessions():
    sessions = read_session_csv()
    return sessions

@router.get("/sessions/{session_id}", response_model=Session)
def get_session_by_id(session_id: int):
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            return session
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.post("/sessions", response_model=Session, status_code=HTTPStatus.CREATED)
def create_session(session: Session):
    sessions = read_session_csv()
    if any(s.id == session.id for s in sessions):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Session with this ID already exists")
    sessions.append(session)
    write_session_csv(sessions)
    return session

@router.put("/sessions/{session_id}", response_model=Session)
def update_session(session_id: int, updated_session: Session):
    sessions = read_session_csv()
    for index, session in enumerate(sessions):
        if session.id == session_id:
            sessions[index] = updated_session
            if updated_session.id != session_id:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            write_session_csv(sessions)
            return updated_session
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.delete("/sessions/{session_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_session(session_id: int):
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            sessions.remove(session)
            write_session_csv(sessions)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

#estrura para verificar rating(validar)
#deixar id gerando automaticamente
#validar se o filme existe antes de criar a sessão
#validar se o filme deletado existe na sessão