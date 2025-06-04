# This file makes the models available for import directly from the 'models' package.
# For example, instead of 'from models.store import StoreModel',
# you can use 'from models import StoreModel'.

from models.item import \
    ItemModel  # Imports the ItemModel class from the item.py file
from models.store import \
    StoreModel  # Imports the StoreModel class from the store.py file
from models.tag import TagModel
from models.item_tags import ItemsTags
from models.user import User
