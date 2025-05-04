import os
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from typing import List
from models.models import Ticket
from datetime import datetime
from .session import read_session_csv

router = APIRouter()
TICKET_CSV_FILE = 'data/ticket.csv'

# Utility functions

def read_ticket_csv() -> List[Ticket]:
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
    tickets = read_ticket_csv()
    return tickets

@router.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket_by_id(ticket_id: int):
    tickets = read_ticket_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            return ticket
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")

@router.post("/tickets", response_model=Ticket, status_code=HTTPStatus.CREATED)
def create_ticket(ticket: Ticket):
    tickets = read_ticket_csv()
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
    tickets = read_ticket_csv()
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
    tickets = read_ticket_csv()
    for ticket in tickets:
        if ticket.id == ticket_id:
            tickets.remove(ticket)
            write_ticket_csv(tickets)
            return
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Ticket not found")