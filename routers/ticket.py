import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from starlette.responses import FileResponse
from typing import List
from models.models import Ticket
from datetime import datetime
from .session import read_session_csv
from utils.logger_config import logger

router = APIRouter()
TICKET_CSV_FILE = 'data/ticket.csv'
TICKET_ZIP_FILE = 'compressed/ticket.zip'

# Utility functions

def read_tickets_csv() -> List[Ticket]:
    tickets: List[Ticket] = []
    if os.path.exists(TICKET_CSV_FILE):
        with open(TICKET_CSV_FILE, mode='r', encoding='utf-8') as file:
            next(file, None) #ignora o header
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


def write_ticket_csv(tickets: List[Ticket]) -> None:
    with open(TICKET_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,session_id,client_name,seat,purchase_date,ticket_type,price\n")
        for ticket in tickets:
            file.write(f"{ticket.id},{ticket.session_id},{ticket.client_name},{ticket.seat},{ticket.purchase_date.isoformat()},{ticket.ticket_type},{ticket.price}\n")

# CRUD Endpoints

@router.get("/tickets", response_model=List[Ticket])
def get_tickets():
    tickets = read_tickets_csv()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket_by_id(ticket_id: int):
    tickets = read_tickets_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            return ticket
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.post("/tickets", response_model=Ticket, status_code=HTTPStatus.CREATED)
def create_ticket(ticket: Ticket):
    tickets = read_tickets_csv()
    if any(t.id == ticket.id for t in tickets):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Ticket with this ID already exists")
    # Verificar se a sessão existe
    sessions = read_session_csv()
    if all(s.id != ticket.session_id for s in sessions):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Session ID does not exist")
    tickets.append(ticket)
    write_ticket_csv(tickets)
    return ticket

@router.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, updated_ticket: Ticket):
    tickets = read_tickets_csv()
    for ind, ticket in enumerate(tickets):
        if ticket.id == ticket_id:
            if updated_ticket.id != ticket_id:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change ticket ID")
            if tickets[ind].session_id != updated_ticket.session_id:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            tickets[ind] = updated_ticket
            write_ticket_csv(tickets)
            return updated_ticket
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.delete("/tickets/{ticket_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_ticket(ticket_id: int):
    tickets = read_tickets_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            tickets.remove(ticket)
            write_ticket_csv(tickets)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.get("/tickets-count")
def get_tickets_count():
    logger.info("Counting all tickets")
    tickets = read_tickets_csv()
    return  {
        "quantidade": len(tickets)
    }

@router.get("/tickets-zip")
def get_tickets_zip():
    logger.info("Creating ZIP file of tickets")
    with zipfile.ZipFile(TICKET_ZIP_FILE, 'w') as zipf:
        zipf.write(TICKET_CSV_FILE, os.path.basename(TICKET_CSV_FILE))
        logger.debug(f"ZIP file created: {TICKET_ZIP_FILE}")
        return FileResponse(TICKET_ZIP_FILE, media_type='application/zip', filename=os.path.basename(TICKET_ZIP_FILE))

@router.get("/tickets-hash")
def get_tickets_hash():
    logger.info("Calculating SHA256 hash of the tickets CSV file")
    sha256_hash = hashlib.sha256()
    with open(TICKET_CSV_FILE, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return {
        "hash_sha256": sha256_hash.hexdigest()
    }

@router.get("/tickets-xml")
def get_tickets_xml():
    logger.info("Converting tickets CSV to XML")
    tickets = read_tickets_csv()
    root = ET.Element("tickets")
    for ticket in tickets:
        ticket_elem = ET.SubElement(root, "ticket")
        for key, value in ticket.dict().items():
            child = ET.SubElement(ticket_elem, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    xml_file_path = 'xml_files/tickets.xml'
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    return FileResponse(xml_file_path, media_type="application/xml", filename=os.path.basename(xml_file_path))