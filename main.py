from models import Product
from fastapi import FastAPI, Depends
from database import session, engine
import db_models
from sqlalchemy.orm import Session
app = FastAPI()
# Use localhost:8000/docs

db_models.base.metadata.create_all(bind=engine)

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

# Main page

@app.get("/")
def greet():
    return "Welcome to Room Rental"

def init_db():
    db: Session = session()
    count = db.query(db_models.Product).count()

    if(count==0):
        for product in products:
            db.add(db_models.Product(**product.model_dump())) # Makes dictionary & unpacks above records only if table empty

    db.commit()
init_db()

# Show all rooms
@app.get("/rooms")
def get_all_rooms(db: Session = Depends(get_db)):
    db_products=db.query(db_models.Product).all()
    return db_products

# Show 1 room
@app.get("/room/{id}")
def room_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()

    if db_product:
        return db_product

    return "Invalid room"
    

# Add room
@app.post("/product")
def add_room(product: Product, db: Session = Depends(get_db)):
    db_product = db_models.Product(**product.model_dump())

    db.add(db_product)
    db.commit()

    return db_product

# Update room
@app.put("/product/")
def update_room(id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()
    if not db_product:
        return {"message": "Invalid room"}

    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price

    db.commit()

    return db_product

# Delete room
@app.delete("/product/{id}")
def delete_room(id: int, db: Session = Depends(get_db)):
    db_product = db.query(db_models.Product).filter(db_models.Product.id == id).first()

    if not db_product:
        return "Invalid room"

    db.delete(db_product)
    db.commit()

    return "Room deleted"