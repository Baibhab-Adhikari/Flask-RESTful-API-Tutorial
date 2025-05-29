# Data Model for item-tag relationship (Many to Many)

from db import db


class ItemsTags(db.Model):  # type: ignore
    __tablename__ = "items_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
