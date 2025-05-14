import os
import zipfile
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse
from http import HTTPStatus
from models.models import Session, Ticket
from typing import List, Optional
from utils.logger_config import logger
from controller.controller import read_movies_csv

router = APIRouter()
from utils.configs import ler_config_yaml

sessions_data = ler_config_yaml().get('data', {})
SESSION_CSV_FILE = sessions_data.get('csv', {}).get('session', 'data/session.csv')
SESSION_ZIP_FILE = sessions_data.get('compressed', {}).get('session', 'compressed/session.zip')

TICKET_CSV_FILE = sessions_data.get('csv', {}).get('ticket', 'data/ticket.csv')
TICKET_ZIP_FILE = sessions_data.get('compressed', {}).get('ticket', 'compressed/ticket.zip')

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
    logger.info("[get_sessions] - Fetching all sessions")
    sessions = read_session_csv()
    logger.info("[get_sessions] - Sessions recovered successfully.")
    return sessions

@router.get("/sessions/{session_id}", response_model=Session)
def get_session_by_id(session_id: int):
    logger.info(f"[get_session_by_id] - Fetching session with ID: {session_id}")
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            logger.info(f"[get_session_by_id] - Session found: {session}")
            return session
    logger.error(f"[get_session_by_id] - Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.post("/sessions", response_model=Session, status_code=HTTPStatus.CREATED)
def create_session(session: Session):
    logger.info(f"[create_session] - Creating session: {session}")
    sessions = read_session_csv()
    if any(s.id == session.id for s in sessions):
        logger.error(f"[create_session] - Session with ID {session.id} already exists")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Session with this ID already exists")
    has_movie = read_movies_csv()
    if all(m.id != int(session.movie_id) for m in has_movie):
        logger.error(f"[create_session] - Movie with ID {session.movie_id} doesn't exists")
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="movie with this id doesn't exists")
    sessions.append(session)
    write_session_csv(sessions)
    logger.info(f"[create_session] - Session created: {session}")
    return session

@router.put("/sessions/{session_id}", response_model=Session)
def update_session(session_id: int, updated_session: Session):
    logger.info(f"[update_session] - Updating session with ID: {session_id}")
    sessions = read_session_csv()
    for index, session in enumerate(sessions):
        if session.id == session_id:
            sessions[index] = updated_session
            if updated_session.id != session_id:
                logger.error(f"[update_session] - Cannot change session ID from {session_id} to {updated_session.id}")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            has_movie = read_movies_csv()
            if all(m.id != int(session.movie_id) for m in has_movie):
                logger.error(f"[create_session] - Movie with ID {session.movie_id} doesn't exists")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="movie with this id doesn't exists")
            write_session_csv(sessions)
            logger.info(f"[update_session] - Session updated: {updated_session}")
            return updated_session
    logger.error(f"[update_session] - Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.delete("/sessions/{session_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_session(session_id: int):
    logger.info(f"[delete_session] - Deleting session with ID: {session_id}")
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            has_ticket = read_tickets_csv()
            print(session_id)
            for ticket in has_ticket:
                if ticket.session_id == int(session_id):
                    print(ticket.session_id)
                    logger.error(f"[delete_session] - Cannot delete session with ID {session_id} because it has associated tickets.")
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot delete session with associated tickets.")
            sessions.remove(session)
            write_session_csv(sessions)
            logger.info(f"[delete_session] - Session deleted: {session}")
            return
    logger.error(f"[delete_session] - Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.get("/sessions-count")
def get_sessions_count():
    logger.info("[get_sessions_count] - Counting all sessions")
    sessions = read_session_csv()
    return  {
        "quantidade": len(sessions)
    }

@router.get("/sessions-zip")
def get_sessions_zip():
    logger.info("[get_sessions_zip] - Creating ZIP file of all sessions")
    with zipfile.ZipFile(SESSION_ZIP_FILE, 'w') as zipf:
        zipf.write(SESSION_CSV_FILE, os.path.basename(SESSION_CSV_FILE))
        return FileResponse(SESSION_ZIP_FILE, media_type="application/zip", filename=os.path.basename(SESSION_ZIP_FILE))

@router.get("/sessions-filter", response_model=List[Session])
def filter_sessions(
    movie_id: Optional[int] = Query(None, description="ID da sessão"),
    room: Optional[str] = Query(None, description="Sala da sessão"),
    start_time_from: Optional[datetime] = Query(None, description="Data/hora de início mínima (ISO format)"),
    start_time_to: Optional[datetime] = Query(None, description="Data/hora de início máxima (ISO format)"),
    available_seat: Optional[str] = Query(None, description="Assento disponível")
):
    logger.info("[filter_sessions] - Starting search with sessions filtering.")
    logger.debug("[filter_sessions] - Filtering attributes:")
    logger.debug(f"[filter_sessions] - movie_id: {movie_id}")
    logger.debug(f"[filter_sessions] - room: {room}")
    logger.debug(f"[filter_sessions] - start_time_from: {start_time_from}")
    logger.debug(f"[filter_sessions] - start_time_to: {start_time_to}")
    logger.debug(f"[filter_sessions] - available_seat: {available_seat}")
    sessions = read_session_csv()
    results: List[Session] = []
    for session in sessions:
        if movie_id is not None and session.movie_id != movie_id:
            continue
        if room is not None and session.room.lower() != room.lower():
            continue
        if start_time_from is not None and session.start_time < start_time_from:
            continue
        if start_time_to   is not None and session.start_time > start_time_to:
            continue
        if available_seat is not None and available_seat not in session.available_seats:
            continue
        results.append(session)
    return results

#F6 Retornar o Hash SHA256 do Arquivo CSV
@router.get("/sessions-hash")
def get_sessions_hash():
    logger.info("[get_sessions_hash - Calculating SHA256 hash of the session CSV file")
    import hashlib
    sha256_hash = hashlib.sha256()
    with open(SESSION_CSV_FILE, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return {
        "hash_sha256": sha256_hash.hexdigest()
    }
                                                                                                                                                                                                                                        
#F8 Converter o csv para xml
@router.get("/sessions-xml")
def get_sessions_xml():
    logger.info("[get_sessions_xml] - Converting sessions CSV to XML")
    import xml.etree.ElementTree as ET
    sessions = read_session_csv()
    root = ET.Element("sessions")
    for session in sessions:
        session_elem = ET.SubElement(root, "session")
        for key, value in session.dict().items():
            child = ET.SubElement(session_elem, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    xml_file_path = sessions_data.get('xml', {}).get('session', 'xml_files/sessions.xml')
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    return FileResponse(xml_file_path, media_type="application/xml", filename=os.path.basename(xml_file_path))