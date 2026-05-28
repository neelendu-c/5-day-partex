from fastapi import FastAPI,APIRouter
from config import collection
from schemas import all_rooms
from models import Product
from bson.objectid import ObjectId



app=FastAPI()
router=APIRouter()

@router.get("/")
async def get_all_rooms():
    data=collection.find()
    return all_rooms(data)

app.include_router(router)

@router.post("/")
async def add_room(new_room: Product):
    response=collection.insert_one(dict(new_room))
    return{"id":str(response.inserted_id)}

app.include_router(router)

@router.put("/{room_id}")
async def update_room(room_id:str, updated_room: Product):
    id=ObjectId(room_id)    
    response=collection.update_one({"_id":id},{"$set":dict(updated_room)})
    return "Updated task"


@router.delete("/{room_id}")
async def delete_room(room_id:str):
    id=ObjectId(room_id)
    response=collection.delete_one({"_id":id})
    return "Deleted task"

app.include_router(router)
