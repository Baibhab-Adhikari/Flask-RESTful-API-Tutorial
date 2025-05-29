# Data Model for stores containing items
from db import db


class StoreModel(db.Model):  # type: ignore
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # This sets up a relationship where each store can have many items.
    # You can access all items in a store using 'store.items'.
    # The 'back_populates="store"' part tells SQLAlchemy this relationship is connected to
    # the 'store' property in the ItemModel — this links both directions (two-way connection).
    # The 'lazy="dynamic"' part means the related items are not loaded immediately with the store.
    # Instead, you get a query object that lets you filter or load items only when needed.
    # Example: store.items.all() will fetch all items in the store.
    items = db.relationship(
        "ItemModel", back_populates="store", lazy="dynamic", cascade="all, delete")
    
    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
 