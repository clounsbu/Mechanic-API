from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func, desc, outerjoin
from application.models import Mechanic, service_mechanic, db
from . import mechanics_bp

# ----------------------ROUTES---------------------------

# Create Mechanic
# Creating an endpoint for api
@mechanics_bp.route("/", methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if there is a Mechanic with this email
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic= db.session.execute(query).scalars().first()
    # If the mechanic email exists return an error message
    if existing_mechanic:
        return jsonify({"Error": "Email already exists."}), 400
    
    # If the mechanic email doesn't exist create the new mechanic
    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201


# Get all Mechanics
@mechanics_bp.route("/", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)


# Get specific mechanic
# Setup endpoint for mechanics
@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
# get mechanic function that takes the mechanic id in to find that mechanic
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

# If the mechanic exists return mechanic schema, if not return an error
    if mechanic:
        return mechanic_schema.jsonify(mechanic)
    return jsonify({"error": "Mechanic not found."}), 400

# Update Specific Mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

# If mechanic is not found return an error
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 400
    
    # Debug: check if request.json exists
    if request.json is None:
        return jsonify({"error": "No JSON data received. Make sure Content-Type header is set to application/json"}), 400
    
    try: 
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Loop over keys and values of mechanic and reset the current information of that mechanic
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# Get mechanics ranked by most tickets worked on
@mechanics_bp.route("/ranked/by-tickets", methods=['GET'])
def get_mechanics_by_tickets():
    # Subquery to count tickets per mechanic
    ticket_count = db.session.query(
        service_mechanic.c.mechanic_id,
        func.count(service_mechanic.c.service_id).label('ticket_count')
    ).group_by(service_mechanic.c.mechanic_id).subquery()
    
    # Main query joining mechanics with the ticket count
    query = db.session.query(Mechanic).outerjoin(
        ticket_count,
        Mechanic.id == ticket_count.c.mechanic_id
    ).order_by(
        desc(func.coalesce(ticket_count.c.ticket_count, 0))
    )
    
    mechanics = query.all()
    return mechanics_schema.jsonify(mechanics)


# Delete specific mechanic
@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 400
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, Successfully deleted'}), 200