import os
from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import PyMongo

load_dotenv()

uri = os.getenv("MONGODB_URI")

app=Flask(__name__)
app.config["MONGO_URI"]=uri
mongo=PyMongo()
mongo.init_app(app)
mongo.db=mongo.cx["rooms_db"]

