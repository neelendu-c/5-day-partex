# Linking
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

db_url="mysql+mysqlconnector://root:password@127.0.0.1:3306/test"
engine=create_engine(db_url)
session=sessionmaker(autocommit=False, bind=engine)

