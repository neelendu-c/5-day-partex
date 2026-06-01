# from pymongo import MongoClient
import os
# from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

load_dotenv()

uri = os.getenv("MONGODB_URI")

mongo=PyMongo()
