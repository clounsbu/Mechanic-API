from application.extensions import ma
from application.models import ServiceTicket


# ----------------------SCHEMAS---------------------------
class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        # Include foreign keys
        include_fk = True


# serializes single customer object
ticket_schema = TicketSchema()
# serializes a list of customers
tickets_schema = TicketSchema(many=True)