from application.extensions import ma
from application.models import Customer
from marshmallow import fields


# ----------------------SCHEMAS---------------------------
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    password = fields.String(load_only=True)  # Accept password on input, but never return it
    
    class Meta:
        model = Customer

# serializes single customer object
customer_schema = CustomerSchema()
# serializes a list of customers
customers_schema = CustomerSchema(many=True)
login_schema = CustomerSchema(exclude=['name', 'phone'])