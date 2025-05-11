import os
import json
import zipfile
import yaml
import logging.config
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse
from http import HTTPStatus
from models.models import Session
from typing import List
from utils.logger_config import logger

router = APIRouter()
SESSION_CSV_FILE = 'data/session.csv'
SESSION_ZIP_FILE = 'compressed/session.zip'

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
    logger.info("Fetching all sessions")
    sessions = read_session_csv()
    return sessions

@router.get("/sessions/{session_id}", response_model=Session)
def get_session_by_id(session_id: int):
    logger.info(f"Fetching session with ID: {session_id}")
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            logger.debug(f"Session found: {session}")
            return session
    logger.error(f"Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.post("/sessions", response_model=Session, status_code=HTTPStatus.CREATED)
def create_session(session: Session):
    logger.info(f"Creating session: {session}")
    sessions = read_session_csv()
    if any(s.id == session.id for s in sessions):
        logger.error(f"Session with ID {session.id} already exists")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Session with this ID already exists")
    sessions.append(session)
    write_session_csv(sessions)
    logger.debug(f"Session created: {session}")
    return session

@router.put("/sessions/{session_id}", response_model=Session)
def update_session(session_id: int, updated_session: Session):
    logger.info(f"Updating session with ID: {session_id}")
    sessions = read_session_csv()
    for index, session in enumerate(sessions):
        if session.id == session_id:
            sessions[index] = updated_session
            if updated_session.id != session_id:
                logger.error(f"Cannot change session ID from {session_id} to {updated_session.id}")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            write_session_csv(sessions)
            logger.debug(f"Session updated: {updated_session}")
            return updated_session
    logger.error(f"Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.delete("/sessions/{session_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_session(session_id: int):
    logger.info(f"Deleting session with ID: {session_id}")
    sessions = read_session_csv()
    for session in sessions:
        if session.id == session_id:
            sessions.remove(session)
            write_session_csv(sessions)
            logger.debug(f"Session deleted: {session}")
            return
    logger.error(f"Session with ID {session_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Session not found")

@router.get("/sessions-count")
def get_sessions_count():
    logger.info("Counting all sessions")
    sessions = read_session_csv()
    return  {
        "quantidade": len(sessions)
    }

@router.get("/sessions-zip")
def get_sessions_zip():
    logger.info("Creating ZIP file of all sessions")
    with zipfile.ZipFile(SESSION_ZIP_FILE, 'w') as zipf:
        zipf.write(SESSION_CSV_FILE, os.path.basename(SESSION_CSV_FILE))
        return FileResponse(SESSION_ZIP_FILE, media_type="application/zip", filename=os.path.basename(SESSION_ZIP_FILE))

@router.get("/sessions-by-attributes", response_model=List[Session])
def get_sessions_by_attribute(
    field: str = Query(..., description="Coluna para busca (e.g. id, movie_id, start_time, room, available_seats)"),
    value: str = Query(..., description="Valor a ser buscado na coluna")
):
    sessions = read_session_csv()
    logger.info(f"Fetching sessions by attribute: {field} with value: {value}")
    
    if field not in Session.__annotations__:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Campo inválido"
        )

    try:
        if field in ["id", "movie_id"]:
            value = int(value)
        elif field == "start_time":
            value = datetime.fromisoformat(value)
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Valor inválido para o campo {field}: {e}"
        )

    filtered = []
    for session in sessions:
        session_value = getattr(session, field)
        
        if field == "available_seats":
            if value in session_value:
                filtered.append(session)
        else:
            if session_value == value:
                filtered.append(session)

    if not filtered:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Nenhuma sessão encontrada com o atributo especificado"
        )
    
    return filtered

#F6 Retornar o Hash SHA256 do Arquivo CSV
@router.get("/sessions-hash")
def get_sessions_hash():
    logger.info("Calculating SHA256 hash of the session CSV file")
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
    logger.info("Converting sessions CSV to XML")
    import xml.etree.ElementTree as ET
    sessions = read_session_csv()
    root = ET.Element("sessions")
    for session in sessions:
        session_elem = ET.SubElement(root, "session")
        for key, value in session.dict().items():
            child = ET.SubElement(session_elem, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    xml_file_path = 'xml_files/sessions.xml'
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    return FileResponse(xml_file_path, media_type="application/xml", filename=os.path.basename(xml_file_path))