# Data Model for items in a store
from db import db


class ItemModel(db.Model):  # type: ignore
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey( 
        "stores.id"), nullable=False)

    # This sets up a relationship where each item is linked to a single store.
    # You can access the store an item belongs to by using 'item.store'.
    # The 'back_populates="items"' part tells SQLAlchemy that the other side of this relationship
    # is the 'items' property in the StoreModel — this creates a two-way connection.
    # So if you add an item to a store's items list, the item’s store is also automatically set.
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship(
        "TagModel", back_populates="items", secondary="items_tags")
