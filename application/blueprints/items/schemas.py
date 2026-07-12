from application.extensions import ma
from application.models import Item


# ----------------------SCHEMAS---------------------------
class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item

# serializes single item object
item_schema = ItemSchema()
# serializes a list of items
items_schema = ItemSchema(many=True)
