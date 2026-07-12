
from application.blueprints.items import items_bp
from application.blueprints.items.schemas import item_schema, items_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Item, ServiceTicket, db
from . import items_bp
from application.utils.util import encode_token, token_required
from application.blueprints.tickets.schemas import tickets_schema




# ----------------------ROUTES---------------------------
# Create Item
# Creating an endpoint for api
@items_bp.route("/", methods=['POST'])

def create_item():
    try:
        item_data = item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_item = Item(item_name=item_data['item_name'], price=item_data['price'])
    db.session.add(new_item)
    db.session.commit()

    return item_schema.jsonify(new_item)
    
    

# Get all items
@items_bp.route("/", methods=['GET'])

def get_items():
    
    query = select(Item)
    result = db.session.execute(query).scalars().all()
    return items_schema.jsonify(result), 200
    
    

# Get specific item
# Setup endpoint for items
@items_bp.route("/<int:item_id>", methods=['GET'])
# get item function that takes the item id in to find that item
def get_item(item_id):
    item = db.session.get(Item, item_id)

# If the item exists return item schema, if not return an error
    if item:
        return item_schema.jsonify(item)
    return jsonify({"error": "Item not found."}), 400

# Update Specific Item
@items_bp.route("/<int:item_id>", methods=['PUT'])

def update_item(item_id):
    item = db.session.get(Item, item_id)


# If item is not found return an error
    if not item:
        return jsonify({"error": "Item not found"}), 400
    
    # Debug: check if request.json exists
    if request.json is None:
        return jsonify({"error": "No JSON data received. Make sure Content-Type header is set to application/json"}), 400
    
    try: 
        item_data = item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Loop over keys and values of item and reset the current information of that item
    for key, value in item_data.items():
        setattr(item, key, value)

    db.session.commit()
    return item_schema.jsonify(item), 200

    # Delete specific item
@items_bp.route("/<int:item_id>", methods=['DELETE'])

# @limiter.limit("5 per day")  # Limit to 5 requests per day
def delete_item(item_id):
    query = select(Item).where(Item.id == item_id)
    item = db.session.execute(query).scalars().first()
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f'Item id: {item_id}, Successfully deleted {item_id}'}), 200

# Get item's service tickets
@items_bp.route("/my-tickets", methods=['GET'])

def get_item_tickets(item_id):
    query = select(ServiceTicket).where(ServiceTicket.item_id == item_id)
    tickets = db.session.execute(query).scalars().all()
    
    if not tickets:
        return jsonify({"message": "No service tickets found for this item."}), 200
    
    return tickets_schema.jsonify(tickets)