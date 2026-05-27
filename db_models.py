# Classes and tables
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

base=declarative_base()

class Product(base):
    __tablename__="roomList"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description= Column(String(255))
    price = Column(Float)
    