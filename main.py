from fastapi import FastAPI, APIRouter, HTTPException, Request
from db_connection import mongo, app
from models import Room, all_rooms
from bson.objectid import ObjectId
from pymongo import ASCENDING,DESCENDING
import httpx
from logger_config import logger
from agent import RoomAgent,SYSTEM_PROMPT

import time
from logs import logger
from fastapi.responses import Response

app = FastAPI()
router = APIRouter()

from models import ChatRequest, ChatRespond


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    
    query_params = dict(request.query_params)
    
    logger.info(
        f"Incoming Request | Method: {request.method} | Path: {request.url.path} | Args: {query_params}"
    )

    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.exception(f"Unhandled crash during request processing: {str(e)}")
        raise e

    duration = time.time() - start_time
    
    logger.info(f"Outgoing Response | Status: {response.status_code} | Time: {duration:.4f}s")
    
    response.headers["X-Execution-Time"] = f"{duration:.4f}s"
    
    return response

agent = RoomAgent(SYSTEM_PROMPT)
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = agent(request.session_id,request.message)
        return ChatRespond(success=True,response=response)
    except httpx.ConnectError:
        logger.exception("Ollama service connectivity failure.")
        raise HTTPException(status_code=503, detail="Ollama service is offline.")
    except Exception as e:
        logger.exception("Error in /chat endpoint")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

app.include_router(router)

@router.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(router)

@router.get("/health")
async def health():
    return {"status":"ok"}    



@router.get("/",operation_id="get_all_rooms")
async def get_all_rooms(page: int):
    perpage=5
    count=mongo.db["rooms-data"].count_documents({})
    if(count<perpage): 
        data = mongo.db["rooms-data"].find()
        return all_rooms(data)
    else: 
        # pagination logic
        start=(page-1)*perpage
        end=start+perpage
        data = mongo.db["rooms-data"].find().skip(start).limit(perpage)
        return all_rooms(data)
    

app.include_router(router)


@router.post("/",operation_id="add_room")
async def add_room(new_room: Room):
    response = mongo.db["rooms-data"].insert_one(dict(new_room))
    return {"id": str(response.inserted_id)}

app.include_router(router)

@router.put("/{room_id}",operation_id="update_orom")
async def update_room(room_id: str, updated_room: Room):
    id = ObjectId(room_id)
    mongo.db["rooms-data"].update_one({"_id": id}, {"$set": dict(updated_room)})
    return "Updated task"

app.include_router(router)

@router.delete("/{room_id}")
async def delete_room(room_id: str):
    id = ObjectId(room_id)
    mongo.db["rooms-data"].delete_one({"_id": id})
    return "Deleted task"

app.include_router(router)

@app.get("/sort") # sort by ascending/descending
async def sort_rooms(sort: int, sortval: str):
    direction = ASCENDING if sort == 1 else DESCENDING
    rooms = mongo.db["rooms-data"].find().sort(sortval, direction)
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
    
    rooms=mongo.db["rooms-data"].find(filter_query)
    return all_rooms(rooms)

app.include_router(router)
