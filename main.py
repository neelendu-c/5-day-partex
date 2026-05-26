from models import Product
from fastapi import FastAPI
app = FastAPI()
# Use localhost:8000/docs

# Main page
@app.get("/")
def greet():
    return "Welcome to Room Rental"

products = [
    Product(id=1,name="House",description="Very good",price=5000),
    Product(id=2,name="House 2",description="Good",price=6000),
    Product(id=500,name="House 3",description="Ok",price=7000)
]

# Show all rooms
@app.get("/rooms")
def get_all_rooms():
    return products

# Show 1 room
@app.get("/room/{id}")
def room_by_id(id: int):
    for product in products:
        if product.id==id:
            return product
    return "invalid product"

# Add room
@app.post("/product")
def add_room(product: Product):
    products.append(product)
    return product

# Update room
@app.put("/product")
def update_room(id:int, product: Product):
    for i in range(len(products)):
        if products[i].id==id:
            products[i] = product
            return "room updated"
    return "Invalid room"

# Delete room
@app.delete("/product")
def delete_room(id:int):
    for i in range(len(products)):
        if products[i].id==id:
            del products[i]
            return "Room deleted"
    return "Invalid room"