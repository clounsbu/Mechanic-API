from application.extensions import ma
from application.models import ServiceTicket
from marshmallow import fields


# ----------------------SCHEMAS---------------------------
class TicketSchema(ma.SQLAlchemyAutoSchema):
    # Show relationships in responses only
    customer = ma.Nested('CustomerSchema', dump_only=True)
    mechanics = ma.Nested('MechanicSchema', many=True, dump_only=True)
    item = ma.Nested('ItemSchema', many=True, dump_only=True)
    
    class Meta:
        model = ServiceTicket
        # Include foreign keys
        include_fk = True


# serializes single customer object
ticket_schema = TicketSchema()
# serializes a list of customers
tickets_schema = TicketSchema(many=True)