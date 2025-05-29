import uuid
from flask import Flask, request
from flask_smorest import abort  # type: ignore
from db import ITEMS, STORES

app = Flask(__name__)


# flask routes


@app.get('/store')  # http://127.0.0.1:5000/store
def get_stores():
    # flask returns 200 as default status code
    return {"stores": list(STORES.values())}


@app.post('/store')
def create_store():
    # Parses and returns JSON data from the request body.
    store_data = request.get_json()

    # again manual data validations...

    if "name" not in store_data:
        abort(
            400, message="Bad request. Ensure that 'name' is included in the JSON payload.")

    for store in STORES.values():
        if store_data["name"] == store["name"]:
            abort(400, message="Store already exists!")

    store_id = uuid.uuid4().hex  # create a new UUID for store
    # create a new store
    store = {**store_data, "id": store_id}  # Python dictionary unpacking!
    STORES[store_id] = store  # add new store to the STORES dict
    return store, 201  # 201 - created HTTP status code


@app.get('/store/<string:store_id>')
def get_specific_store(store_id):
    try:
        return STORES[store_id]
    except KeyError:
        abort(404, message="Store not found!")


@app.delete("/store/<string:store_id>")
def delete_specific_store(store_id):
    try:
        del STORES[store_id]
        return {"message": "Store successfully deleted!"}

    except KeyError:
        abort(404, message="Store not found!")


@app.post('/item')
def create_item():
    item_data = request.get_json()  # get JSON data from the request body

    # initial input validation with if statements:

    # check for missing data in JSON payload

    if ("price" not in item_data
                or "store_id" not in item_data
                or "name" not in item_data
            ):
        abort(400,
              message="Bad Request. Ensure 'price', 'store_id' and 'name' are included in the JSON payload. "
              )

    # check for duplicate items
    for item in ITEMS.values():
        if item_data["name"] == item["name"] and item_data["store_id"] == item["store_id"]:
            abort(400, message="Item already exists!")

    # check if store not found

    if item_data["store_id"] not in STORES:
        # proper error handling with flask-smorest
        abort(404, message="Store not found!")

    # creating new item
    item_id = uuid.uuid4().hex
    item = {**item_data, "id": item_id}
    ITEMS[item_id] = item  # add new item to the ITEMS dict
    return item, 201


@app.get("/item")
def get_all_items():
    return {"items": list(ITEMS.values())}


@app.get('/item/<string:item_id>')
def get_specific_item(item_id):
    try:
        return ITEMS[item_id]
    except KeyError:
        abort(404, message="Item not found!")


@app.delete("/item/<string:item_id>")
def delete_specific_item(item_id):
    try:
        del ITEMS[item_id]  # delete the key and its associated value.
        return {"message": "Item deleted!"}

    except KeyError:
        abort(404, message="Item not found!")


@app.put("/item/<string:item_id>")
def update_specific_item(item_id):
    item_data = request.get_json()

    if "price" not in item_data or "name" not in item_data:
        abort(
            400, message="Bad Request. Ensure 'name' or 'price' is present in JSON payload!")

    try:
        item = ITEMS[item_id]
        # dictionary update operator (modifies dict in place)
        item |= item_data
        return {**item, "message": "Item successfully updated!"}
    except KeyError:
        abort(404, message="Item not found!")
