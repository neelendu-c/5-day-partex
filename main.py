from fastapi import FastAPI, APIRouter
from config import collection
from schemas import all_rooms
from models import Product
from bson.objectid import ObjectId
from pymongo import ASCENDING,DESCENDING

app = FastAPI()
router = APIRouter()


@router.get("/",operation_id="get_all_rooms")
async def get_all_rooms(page: int):
    perpage=3
    count=collection.count_documents({})
    if(count<perpage): 
        data = collection.find()
        return all_rooms(data)
    else: 
        # pagination logic
        start=(page-1)*perpage
        end=start+perpage
        data = collection.find().skip(start).limit(perpage)
        return all_rooms(data)

app.include_router(router)

@router.post("/",operation_id="add_room")
async def add_room(new_room: Product):
    response = collection.insert_one(dict(new_room))
    return {"id": str(response.inserted_id)}

app.include_router(router)

@router.put("/{room_id}",operation_id="update_orom")
async def update_room(room_id: str, updated_room: Product):
    id = ObjectId(room_id)
    collection.update_one({"_id": id}, {"$set": dict(updated_room)})
    return "Updated task"

app.include_router(router)

@router.delete("/{room_id}")
async def delete_room(room_id: str):
    id = ObjectId(room_id)
    collection.delete_one({"_id": id})
    return "Deleted task"

app.include_router(router)

@app.get("/sort") # sort by ascending/descending
async def sort_rooms(sort: int, sortval: str):
    direction = ASCENDING if sort == 1 else DESCENDING
    rooms = collection.find().sort(sortval, direction)
    return all_rooms(rooms)

app.include_router(router)

@app.get("/filter")
# 1 for gt, 2 for lt, 3 for e, 4 for all
async def filter_rooms(filter: str, filtertype: str, type: int):
    filtertype=int(filtertype) if filter=="price" else None

    if(type==4):
        filter_query={filter: filtertype}
    elif(type==3):
        filter_query={filter: {"$e":filtertype}}
    elif(type==2):
        filter_query={filter: {"$lt":filtertype}}
    elif(type==1):
        filter_query={filter: {"$gt":filtertype}}
    else:
        return "Invalid input"
    
    rooms=collection.find(filter_query)
    return all_rooms(rooms)

app.include_router(router)

