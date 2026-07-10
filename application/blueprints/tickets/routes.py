from .schemas import ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import ServiceTicket, db
from . import tickets_bp

# ----------------------ROUTES---------------------------

# Create Ticket
# Creating an endpoint for api
@tickets_bp.route("/", methods=['POST'])
def create_ticket():
    try:
        ticket_data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    
    
    new_ticket = ServiceTicket(**ticket_data)
    db.session.add(new_ticket)
    db.session.commit()
    return ticket_schema.jsonify(new_ticket), 201


# Get all Tickets
@tickets_bp.route("/", methods=['GET'])
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()

    return tickets_schema.jsonify(tickets)


# Get specific ticket
# Setup endpoint for tickets
@tickets_bp.route("/<int:ticket_id>", methods=['GET'])
# get ticket function that takes the ticket id in to find that ticket
def get_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

# If the ticket exists return ticket schema, if not return an error
    if ticket:
        return ticket_schema.jsonify(ticket)
    return jsonify({"error": "Ticket not found."}), 400

# Update Specific Ticket
@tickets_bp.route("/<int:ticket_id>", methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

# If ticket is not found return an error
    if not ticket:
        return jsonify({"error": "Customer not found"}), 400
    
    # Debug: check if request.json exists
    if request.json is None:
        return jsonify({"error": "No JSON data received. Make sure Content-Type header is set to application/json"}), 400
    
    try: 
        ticket_data = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Loop over keys and values of ticket and reset the current information of that ticket
    for key, value in ticket_data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200
