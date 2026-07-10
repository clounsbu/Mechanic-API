from application.extensions import ma
from application.models import Mechanic


# ----------------------SCHEMAS---------------------------
class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic

# serializes single customer object
mechanic_schema = MechanicSchema()
# serializes a list of customers
mechanics_schema = MechanicSchema(many=True)