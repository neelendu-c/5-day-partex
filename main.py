from flask import Flask,request,jsonify,g 
from flask_pymongo import PyMongo
from db_connection import uri,mongo
from flasgger import Swagger, swag_from
from middleware import swagger_config,template
import jwt
import time

app=Flask(__name__)
app.config["MONGO_URI"]=uri
mongo.init_app(app)
mongo.db=mongo.cx["rooms_db"]
Swagger(app, config=swagger_config, template=template)

@app.before_request
def before_request():
    g.start_time = time.time()

    print(f"\nIncoming Request")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Args: {dict(request.args)}")


@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    print(f"Status: {response.status_code}")
    print(f"Time: {duration:.4f}s")
    response.headers["X-Execution-Time"] = str(duration)

    return response

    

# print("URI:", uri)
# print("Mongo:", mongo)
# print("Mongo DB:", mongo.db)

# @app.route("/verify/{token}",methods=['GET'])
# @swag_from("swagger_docs/verify.yml")
# def verify():
#     token=request.args.get('token','1')
#     try:
#         payload=jwt.decode(token,"testkey",algorithm=['HS256'])
#         return payload
#     except jwt.InvalidKeyError:
#         print("Invalid key")
#     except:
#         print("Error processing token")
#     return {}
    
@app.route("/test", methods=['GET'])
@swag_from("swagger_docs/test.yml")
def recs():
    size = int(request.args.get('size', 1))
    return {"result": "test" * size}

@app.route("/show",methods=["GET"])
@swag_from("swagger_docs/show.yml")
def show():
    page = int(request.args.get('page',1))
    perpage=3
    count=mongo.db["rooms-data"].count_documents({})
    if(count<perpage): 
        data = mongo.db["rooms-data"].find({})
        return jsonify(data)
    else: 
        # pagination logic
        start=(page-1)*perpage
        data = mongo.db["rooms-data"].find({}).skip(start).limit(perpage)
        return jsonify(data)

@app.route("/insert", methods=['PUT'])
@swag_from("swagger_docs/insert.yml")
def insert_one():
    id=int(request.args.get('id',1))
    name=str(request.args.get('name',1))
    desc=str(request.args.get('desc',1))
    price=int(request.args.get('price',1))
    room={'id': id, 'name': name,'description': desc,'price': price}
    mongo.db["rooms-data"].insert_one(room)
    return{"result": "Room added successfully"}



@app.route("/update", methods=['PUT'])
@swag_from("swagger_docs/update.yml")
def update():
    id=int(request.args.get('id',1))
    name=str(request.args.get('name',1))
    desc=str(request.args.get('desc',1))
    price=int(request.args.get('price',1))
    room={'id': id, 'name': name,'description': desc,'price': price}
    mongo.db["rooms-data"].update_one({"id": id}, {"$set": dict(room)})
    return {"result": "Updated room"}



@app.route("/sort", methods=['GET'])
@swag_from("swagger_docs/sort.yml")
def sort():
    direction=int(request.args.get('direction',1))
    sortval=request.args.get('sortval',1)
    rooms = mongo.db["rooms-data"].find().sort(sortval, direction)
    data=list(rooms)
    return jsonify(data)



@app.route("/delete", methods=['DELETE'])
@swag_from("swagger_docs/delete.yml")
def delete():
    id=int(request.args.get('id',1))
    mongo.db["rooms-data"].delete_one({"id": id})
    return {"result": "Deleted task"}




@app.route("/filter", methods=['GET'])
@swag_from("swagger_docs/filter.yml")
def filtering():
    type=int(request.args.get('id',1))
    filter=request.args.get('filter',1)
    filtertype=request.args.get('filtertype',1)
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
    return jsonify(rooms)



if __name__== '__main__':
    app.run(debug=True)

# from fastapi import FastAPI, APIRouter
# from config import collection
# from schemas import all_rooms
# from models import Product
# from bson.objectid import ObjectId
# from pymongo import ASCENDING,DESCENDING

# app = FastAPI()
# router = APIRouter()


# @router.get("/",operation_id="get_all_rooms")
# async def get_all_rooms(page: int):
#     perpage=3
#     count=collection.count_documents({})
#     if(count<perpage): 
#         data = collection.find()
#         return all_rooms(data)
#     else: 
#         # pagination logic
#         start=(page-1)*perpage
#         end=start+perpage
#         data = collection.find().skip(start).limit(perpage)
#         return all_rooms(data)

# app.include_router(router)

# @router.post("/",operation_id="add_room")
# async def add_room(new_room: Product):
#     response = collection.insert_one(dict(new_room))
#     return {"id": str(response.inserted_id)}

# app.include_router(router)

# @router.put("/{room_id}",operation_id="update_orom")
# async def update_room(room_id: str, updated_room: Product):
#     id = ObjectId(room_id)
#     collection.update_one({"_id": id}, {"$set": dict(updated_room)})
#     return "Updated task"

# app.include_router(router)

# @router.delete("/{room_id}")
# async def delete_room(room_id: str):
#     id = ObjectId(room_id)
#     collection.delete_one({"_id": id})
#     return "Deleted task"

# app.include_router(router)

# @app.get("/sort") # sort by ascending/descending
# async def sort_rooms(sort: int, sortval: str):
#     direction = ASCENDING if sort == 1 else DESCENDING
#     rooms = collection.find().sort(sortval, direction)
#     return all_rooms(rooms)

# app.include_router(router)

# @app.get("/filter")
# # 1 for gt, 2 for lt, 3 for e, 4 for all
# async def filter_rooms(filter: str, filtertype: str, type: int):
#     filtertype=int(filtertype) if filter=="price" else None

#     if(type==4):
#         filter_query={filter: filtertype}
#     elif(type==3):
#         filter_query={filter: {"$e":filtertype}}
#     elif(type==2):
#         filter_query={filter: {"$lt":filtertype}}
#     elif(type==1):
#         filter_query={filter: {"$gt":filtertype}}
#     else:
#         return "Invalid input"
    
#     rooms=collection.find(filter_query)
#     return all_rooms(rooms)

# app.include_router(router)

