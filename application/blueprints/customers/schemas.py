from application.extensions import ma
from application.models import Customer


# ----------------------SCHEMAS---------------------------
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer

# serializes single customer object
customer_schema = CustomerSchema()
# serializes a list of customers
customers_schema = CustomerSchema(many=True)