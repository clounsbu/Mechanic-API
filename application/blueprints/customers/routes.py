
from application.blueprints.customers import customers_bp
from application.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify, session
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customer, ServiceTicket, db
from . import customers_bp
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required
from application.blueprints.tickets.schemas import tickets_schema

# ----------------------ROUTES---------------------------
@customers_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    email = credentials.get('email')
    password = credentials.get('password')
    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400
    
    query = select(Customer). where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)

        response = {
            "status": "Success",
            "message": "successfully logged in.",
            "token": token
        }

        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 400


# Create Customer
# Creating an endpoint for api
@customers_bp.route("/", methods=['POST'])
@limiter.limit("5 per day")  # Limit to 5 requests per day
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
@cache.cached(timeout=60)  # Cache the response at 60 seconds
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = select(Customer)
    # Use paginate for pagination
    pagination = db.paginate(query, page=page, per_page=per_page)
    customers = pagination.items
    
    response = {
        "customers": customers_schema.dump(customers),
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
        "per_page": per_page
    }
    
    return jsonify(response)

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
@customers_bp.route("/", methods=['PUT'])
@token_required
@limiter.limit("5 per month")  # Limit to 5 requests per month
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
@customers_bp.route("/", methods=['DELETE'])
@token_required
@limiter.limit("5 per day")  # Limit to 5 requests per day
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, Successfully deleted'}), 200

# Get customer's service tickets
@customers_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_customer_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    
    if not tickets:
        return jsonify({"message": "No service tickets found for this customer."}), 200
    
    return tickets_schema.jsonify(tickets)