from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customer, db
from . import customers_bp

# ----------------------ROUTES---------------------------

# Create Customer
# Creating an endpoint for api
@customers_bp.route("/", methods=['POST'])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if there is a customer with this email
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_member = db.session.execute(query).scalars().first()
    # If the customer email exists return an error message
    if existing_member:
        return jsonify({"Error": "Email already exists."}), 400
    
    # If the customer email doesn't exist create the new customer
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201


# Get all Customers
@customers_bp.route("/", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)


# Get specific customer
# Setup endpoint for customers
@customers_bp.route("/<int:customer_id>", methods=['GET'])
# get customer function that takes the customer id in to find that customer
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

# If the customer exists return customer schema, if not return an error
    if customer:
        return customer_schema.jsonify(customer)
    return jsonify({"error": "Customer not found."}), 400

# Update Specific Customer
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

# If customer is not found return an error
    if not customer:
        return jsonify({"error": "Customer not found"}), 400
    
    # Debug: check if request.json exists
    if request.json is None:
        return jsonify({"error": "No JSON data received. Make sure Content-Type header is set to application/json"}), 400
    
    try: 
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Loop over keys and values of customer and reset the current information of that customer
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200


    # Delete specific customer
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 400
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, Successfully deleted'}), 200