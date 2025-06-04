from marshmallow import Schema, fields


# Defines the basic schema for an item, used for creating or displaying an item without store relationship details.
class PlainItemSchema(Schema):
    # Item ID: Read-only, only included when serializing (Python object -> JSON).
    id = fields.Int(dump_only=True)
    # Item name: Required field for both input (JSON -> Python object) and output.
    name = fields.Str(required=True)
    # Item price: Required field for both input and output.
    price = fields.Float(required=True)


# Defines the basic schema for a store, used for displaying a store without its list of items.
class PlainStoreSchema(Schema):
    # Store ID: Read-only, only included when serializing.
    id = fields.Int(dump_only=True)
    # Store name: Required field for input and output.
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


# Defines the full schema for an item, including its relationship with a store. Inherits from PlainItemSchema.
class ItemSchema(PlainItemSchema):
    # Store ID: Required when creating/updating an item (loading JSON), but not included when displaying the item (dumping to JSON).
    store_id = fields.Int(required=True, load_only=True)
    # Nested store information: Includes the full store details (using PlainStoreSchema) when displaying an item. Read-only.
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

# Defines the schema for updating an existing item. Allows partial updates (name or price or both).


class ItemUpdateSchema(Schema):
    # Item name: Optional. If provided, the item's name will be updated.
    name = fields.Str()
    # Item price: Optional. If provided, the item's price will be updated.
    price = fields.Float()
    store_id = fields.Int()  # Store ID for the item, it is optional.


# Defines the full schema for a store, including its list of items. Inherits from PlainStoreSchema.
class StoreSchema(PlainStoreSchema):
    # List of items: Includes a list of items (using PlainItemSchema for each) associated with the store when displaying store details. Read-only.
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

# User marshmallow schema


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True)
