from pymongo import MongoClient
import os
from pymongo.server_api import ServerApi
from dotenv import load_dotenv,dotenv_values

load_dotenv()

uri = os.getenv("URI")

client = MongoClient(uri, server_api=ServerApi('1'))

db=client.rooms_db
collection=db["rooms-data"]