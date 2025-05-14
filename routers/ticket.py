import os
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from fastapi import APIRouter, HTTPException, Query
from http import HTTPStatus
from starlette.responses import FileResponse
from typing import List, Optional
from models.models import Ticket
from datetime import datetime
from .session import read_session_csv
from utils.logger_config import logger

router = APIRouter()
from utils.configs import ler_config_yaml

tickets_data = ler_config_yaml().get('data', {})
TICKET_CSV_FILE = tickets_data.get('csv', {}).get('ticket', 'data/ticket.csv')
TICKET_ZIP_FILE = tickets_data.get('compressed', {}).get('ticket', 'compressed/ticket.zip')

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


def write_ticket_csv(tickets: List[Ticket]) -> None:
    with open(TICKET_CSV_FILE, mode='w', encoding='utf-8') as file:
        file.write("id,session_id,client_name,seat,purchase_date,ticket_type,price\n")
        for ticket in tickets:
            file.write(f"{ticket.id},{ticket.session_id},{ticket.client_name},{ticket.seat},{ticket.purchase_date.isoformat()},{ticket.ticket_type},{ticket.price}\n")

# CRUD Endpoints

@router.get("/tickets", response_model=List[Ticket])
def get_tickets():
    logger.info("[get_tickets] - Fetching all tickets")
    tickets = read_tickets_csv()
    logger.debug(f"[get_tickets] - {len(tickets)} tickets found")
    logger.info("[get_tickets] - Tickets recovered successfully.")
    return tickets

@router.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket_by_id(ticket_id: int):
    logger.info(f"[get_ticket_by_id] - Fetching ticket with ID: {ticket_id}")
    tickets = read_tickets_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            logger.info(f"[get_ticket_by_id] - Ticket found: {ticket}")
            return ticket
    logger.error(f"[get_ticket_by_id] - Ticket with ID {ticket_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.post("/tickets", response_model=Ticket, status_code=HTTPStatus.CREATED)
def create_ticket(ticket: Ticket):
    logger.info(f"[create_ticket] - Creating ticket: {ticket}")
    tickets = read_tickets_csv()
    if any(t.id == ticket.id for t in tickets):
        logger.error(f"[create_ticket] - Ticket with ID {ticket.id} already exists")
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Ticket with this ID already exists")
    sessions = read_session_csv()
    if all(s.id != ticket.session_id for s in sessions):
        logger.error(f"[create_ticket] - Session ID {ticket.session_id} does not exist")
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Session ID does not exist")
    tickets.append(ticket)
    write_ticket_csv(tickets)
    logger.info(f"[create_ticket] - Ticket created: {ticket}")
    return ticket

@router.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: int, updated_ticket: Ticket):
    logger.info(f"[update_ticket] - Updating ticket with ID: {ticket_id}")
    tickets = read_tickets_csv()
    for ind, ticket in enumerate(tickets):
        if ticket.id == ticket_id:
            if updated_ticket.id != ticket_id:
                logger.error("[update_ticket] - Cannot change ticket ID")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change ticket ID")
            if tickets[ind].session_id != updated_ticket.session_id:
                logger.error("[update_ticket] - Cannot change session ID")
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cannot change session ID")
            tickets[ind] = updated_ticket
            write_ticket_csv(tickets)
            logger.info(f"[update_ticket] - Ticket updated: {updated_ticket}")
            return updated_ticket
    logger.error(f"[update_ticket] - Ticket with ID {ticket_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.delete("/tickets/{ticket_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_ticket(ticket_id: int):
    logger.info(f"[delete_ticket] - Deleting ticket with ID: {ticket_id}")
    tickets = read_tickets_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            tickets.remove(ticket)
            write_ticket_csv(tickets)
            logger.info(f"[delete_ticket] - Ticket deleted: {ticket}")
            return
    logger.error(f"[delete_ticket] - Ticket with ID {ticket_id} not found")
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.get("/tickets-count")
def get_tickets_count():
    logger.info("[get_tickets_count] - Counting all tickets")
    tickets = read_tickets_csv()
    return {"quantidade": len(tickets)}

@router.get("/tickets-zip")
def get_tickets_zip():
    logger.info("[get_tickets_zip] - Creating ZIP file of tickets")
    with zipfile.ZipFile(TICKET_ZIP_FILE, 'w') as zipf:
        zipf.write(TICKET_CSV_FILE, os.path.basename(TICKET_CSV_FILE))
        logger.info(f"[get_tickets_zip] - ZIP file created: {TICKET_ZIP_FILE}")
    return FileResponse(TICKET_ZIP_FILE, media_type='application/zip', filename=os.path.basename(TICKET_ZIP_FILE))

@router.get("/tickets-filter", response_model=List[Ticket])
def filter_tickets(
    session_id: Optional[int] = Query(None, description="ID da sessão"),
    ticket_type: Optional[str] = Query(None, description="Tipo de ingresso (Normal, Meia-entrada, Promocional)"),
    client_name: Optional[str] = Query(None, description="Nome do cliente"),
    seat: Optional[str] = Query(None, description="Cadeira"),
    min_price: Optional[float] = Query(None, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, description="Preço máximo")
):
    logger.info("[filter_tickets] - Starting search with tickets filtering.")
    logger.debug("[filter_tickets] - Filtering attributes:")
    logger.debug(f"[filter_tickets] - session_id: {session_id}")
    logger.debug(f"[filter_tickets] - ticket_type: {ticket_type}")
    logger.debug(f"[filter_tickets] - client_name: {client_name}")
    logger.debug(f"[filter_tickets] - seat: {seat}")
    logger.debug(f"[filter_tickets] - min_price: {min_price}")
    logger.debug(f"[filter_tickets] - max_price: {max_price}")
    tickets = read_tickets_csv()
    results: List[Ticket] = []
    for ticket in tickets:
        if session_id is not None and ticket.session_id != session_id:
            continue
        if ticket_type is not None and ticket.ticket_type.lower() != ticket_type.lower():
            continue
        if client_name is not None and client_name.lower() not in ticket.client_name.lower():
            continue
        if seat is not None and seat.lower() not in ticket.seat.lower():
            continue
        if min_price is not None and ticket.price < min_price:
            continue
        if max_price is not None and ticket.price > max_price:
            continue
        results.append(ticket)
    return results

@router.get("/tickets-hash")
def get_tickets_hash():
    logger.info("[get_tickets_hash] - Calculating SHA256 hash of the tickets CSV file.")
    sha256_hash = hashlib.sha256()
    with open(TICKET_CSV_FILE, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return {"hash_sha256": sha256_hash.hexdigest()}

@router.get("/tickets-xml")
def get_tickets_xml():
    logger.info("[get_tickets_xml] - Converting tickets CSV to XML")
    tickets = read_tickets_csv()
    root = ET.Element("tickets")
    for ticket in tickets:
        ticket_elem = ET.SubElement(root, "ticket")
        for key, value in ticket.dict().items():
            child = ET.SubElement(ticket_elem, key)
            child.text = str(value)
    tree = ET.ElementTree(root)
    xml_file_path = tickets_data.get('xml', {}).get('ticket', 'xml_files/tickets.xml')
    tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
    return FileResponse(xml_file_path, media_type='application/xml', filename=os.path.basename(xml_file_path))