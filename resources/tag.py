from flask.views import MethodView
from flask_smorest import Blueprint, abort  # type: ignore
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel, StoreModel, TagModel
from schemas import TagAndItemSchema, TagSchema

blp = Blueprint("Tags", "tags", description="Operations on Tags")


@blp.route("/store/<string:store_id>/tags")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        """
        List of tags that are created under a store.
        """

        store = StoreModel.query.get_or_404(store_id)
        # Accesses the 'tags' related to the fetched 'store' and retrieves all of them.
        # This works because of the 'tags' relationship defined in the StoreModel. (lazy=dynamic is also set)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def post(self, tag_data, store_id):
        """Method to create new tags under a particular store."""

        # passing store_id explicitly because in the model store_id is dump only
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, exc=str(e))

        return tag


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(200, TagSchema)
    def post(self, item_id, tag_id):
        """Links/adds a tag to an item"""
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        # Appends the fetched tag to the item's list of tags.
        # This works due to the many-to-many relationship defined in the models.
        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, exc="An error occured while inserting the tag.")

        return tag

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        """unlinks/removes a tag from an item"""
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        # Removes the specified tag from the item's list of tags.
        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, exc="An error occured while removing the tag from the item.")

        return {
            "message": "Item removed from the tag",
            "item": item,
            "tag": tag
        }


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """Lists details of a particular tag"""
        tag = TagModel.query.get_or_404(tag_id)

        return tag

    # Decorator for the DELETE method: Specifies a 202 Accepted response if deletion is successful.
    # It also includes a description and an example for the API documentation.
    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it.",
        example={"message": "Tag deleted."},
    )
    # Alternative response decorator: Specifies a 404 Not Found response if the tag doesn't exist.
    @blp.alt_response(404, description="Tag not found.")
    # Alternative response decorator: Specifies a 400 Bad Request response if the tag is still linked to items.
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.",
    )
    def delete(self, tag_id):
        """Deletes a particular tag from the DB"""
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}

        abort(400, exc="Could not delete tag. Make sure the tag is not associated with any items before trying again.")
