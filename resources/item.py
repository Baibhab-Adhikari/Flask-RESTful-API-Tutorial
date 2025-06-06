from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort  # type: ignore
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("Items", __name__, description="Operations on ITEMS.")


# registers this Item class as the handler for /item/<item_id>
@blp.route("/item/<string:item_id>")
class Item(MethodView):  # contains all HTTP methods (mapped to the methods) for /item/<item_id>
    @jwt_required()  # jwt token required to access this route and method
    @blp.response(200, ItemSchema)  # updates the docs, returns status code
    # Serialize the response using ItemSchema and return HTTP 200 OK to the API client
    def get(self, item_id):
        # get the item by its id, or return 404
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):

        # using the JWT claims
        # Retrieve the entire decoded JWT payload (claims) from the current request.
        jwt = get_jwt()
        # Check for a custom claim 'is_admin' in the JWT.
        # This claim would have been added when the token was created, indicating user privileges.
        if not jwt.get("is_admin"):
            abort(401, exc="Admin privilege required.")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted successfully!"}

    @blp.arguments(ItemUpdateSchema)
    # response decorator should be nested deeper!
    @blp.response(200, ItemSchema)
    # injected args will come first, then the url args
    def put(self, item_data, item_id):
        """
        This operation is idempotent. This means that making the same PUT request
        multiple times to the same item_id will have the same effect as making
        it once. The item will either be updated to the new state, or created
        if it wasn't there, but repeated calls won't create multiple items or
        cause other side effects.
        """
        item = ItemModel.query.get(item_id)

        # check if item exist in DB
        if item:
            # access the columns and update the injected data
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            # upack the dict into kwargs
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        return item


# Registers this ItemList class as the handler for /item routes


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required(fresh=True)  # this endpoint requires a fresh token
    # many=True indicates that the response will be a list of items!
    @blp.response(200, ItemSchema(many=True))
    # Handles GET requests to /item
    def get(self):
        return ItemModel.query.all()  # returns all the records in the item table

    @jwt_required()
    # Validates incoming JSON against ItemSchema
    # If validation passes, the deserialized data is injected as `item_data`
    # If validation fails, Flask-Smorest automatically returns a 400 Bad Request with an error message
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    # Defines the handler for POST requests to "/item", 'item_data' is the validated request body.
    def post(self, item_data):
        # Creates a new ItemModel instance, unpacking item_data dict as keyword arguments.
        item = ItemModel(**item_data)

        try:
            # Adds the new item object to the database session.
            db.session.add(item)
            # Saves the changes in the session to the database.
            db.session.commit()
        # Catches any SQLAlchemy-related errors during database operation.
        except SQLAlchemyError:
            # Returns a 500 Internal Server Error if an issue occurs.
            abort(500, message="An error occurred while inserting the item.")
        return item  # Returns the newly created item.
