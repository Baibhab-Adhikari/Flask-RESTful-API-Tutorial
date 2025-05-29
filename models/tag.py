# Data Model for tags linked to a store
from db import db


class TagModel(db.Model):  # type: ignore
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey(
        "stores.id"), nullable=False)
    store = db.relationship("StoreModel", back_populates="tags")
    items = db.relationship(
        "ItemModel", back_populates="tags", secondary="items_tags")
    # 'secondary="items_tags"' specifies the association table that links tags and items.
