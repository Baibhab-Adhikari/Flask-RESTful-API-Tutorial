from flask.views import MethodView
from flask_smorest import Blueprint, abort  # type: ignore
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import StoreModel
from schemas import StoreSchema

# blueprint object for routes related to STORES
blp = Blueprint("Stores", __name__, description="Operations on STORES.")


@blp.route("/store/<string:store_id>")
class Store(MethodView):  # this class contains all the HTTP methods for /store/<store_id>
    @blp.response(200, StoreSchema)
    def get(self, store_id):  # handles GET at /store/<store_id>
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):  # handles DELETE at /store/<store_id>
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)  # passing the instance to delete from the DB
        db.session.commit()
        return {"message": "Store deleted successfully!"}


@blp.route("/store")
class StoreList(MethodView):  # contains all the HTTP methods for /store
    @blp.response(200, StoreSchema(many=True))
    def get(self):  # handles GET at /store
        return StoreModel.query.all()  # returns all the records of the store table

    # deserialized data will be injected by the StoreSchema!
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):

        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, exc="A store with that name already exists.")
        except SQLAlchemyError:
            abort(500, exc="An error occured while creating the store.")

        return store
