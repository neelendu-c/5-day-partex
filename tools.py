from db_connection import mongo
import re
import json
from ollama import chat
from pymongo import UpdateOne
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from db_connection import uri
from pymongo import MongoClient
from vector_search import show_rooms


def create_rooms(action_input):
    if not action_input:
        return {"error": "No input provided"}

    if isinstance(action_input, dict) and "rooms" in action_input:
        rooms_list = action_input["rooms"]
    elif isinstance(action_input, list):
        rooms_list = action_input
    elif isinstance(action_input, dict):
        rooms_list = [action_input]  
    else:
        return {"error": "Invalid input format."}
        
    if not rooms_list:
        return {"error": "No rooms matching criteria"}
        
    for room in rooms_list:
        if "_id" in room and "id" not in room:
            room["id"] = room.pop("_id")
            
        if "id" in room and str(room["id"]).isdigit():
            room["id"] = int(room["id"])
            
    try:
        result = mongo.db["rooms-data"].insert_many(rooms_list)
        return {"result": f"Created {len(result.inserted_ids)} rooms.", "ids": [str(i) for i in result.inserted_ids]}
    except Exception as e:
        return {"error": f"Database insertion failed: {str(e)}"}

def update_rooms(action_input):
    if not action_input:
        return {"error": "Could not be parsed as valid JSON."}

    if isinstance(action_input, list):
        operations = []
        for item in action_input:
            query_filter = item.get("filter", {})
            update_data = item.get("update", {})
            
            if "id" in query_filter:
                query_filter["id"] = int(query_filter["id"]) if str(query_filter["id"]).isdigit() else query_filter["id"]
                
            operations.append(UpdateOne(query_filter, update_data))
        
        if not operations:
            return {"error": "No valid operations found in list."}
            
        print(f"--- EXECUTING MONGO BULK UPDATE | {len(operations)} operations ---")
        result = mongo.db["rooms-data"].bulk_write(operations)
        return {
            "matched_count": result.matched_count, 
            "modified_count": result.modified_count,
            "status": "Bulk update successful"
        }

    query_filter = action_input.get("filter", {})
    update_data = action_input.get("update", {})

    if not query_filter and not update_data:
        extracted_filter = {}
        extracted_update = {}
        
        for k, v in action_input.items():
            if k in ["id", "_id", "room_id"]:
                target_key = "id" if k != "_id" else "_id"
                if isinstance(v, list):
                    extracted_filter[target_key] = {"$in": [int(i) if str(i).isdigit() else i for i in v]}
                else:
                    extracted_filter[target_key] = int(v) if str(v).isdigit() else v
            elif k != "$set":
                extracted_update[k] = v
        
        query_filter = extracted_filter
        if extracted_update:
            update_data = {"$set": extracted_update}

    if update_data and not any(key.startswith("$") for key in update_data.keys()):
        update_data = {"$set": update_data}

    if not query_filter or not update_data:
        return {"error": f"Failed to map input structure to valid Mongo parameters. Received: {action_input}"}
        
    print(f"--- EXECUTING MONGO UPDATE | Filter: {query_filter} | Update: {update_data} ---")
    result = mongo.db["rooms-data"].update_many(query_filter, update_data)
    
    return {
        "matched_count": result.matched_count, 
        "modified_count": result.modified_count,
        "status": "Success" if result.matched_count > 0 else "No matching rooms found"
    }



def delete_rooms(action_input):
    if not action_input:
        return {"error": "No input provided"}

    if isinstance(action_input, list):
        total_deleted = 0
        for item in action_input:
            result = delete_rooms(item)
            if "deleted_count" in result:
                total_deleted += result["deleted_count"]
        return {
            "deleted_count": total_deleted,
            "status": f"Batch delete finished. Total removed: {total_deleted}"
        }

    query_filter = action_input.get("filter", {})
    
    if not query_filter:
        query_filter = action_input

    final_filter = {}
    for k, v in query_filter.items():
        if k in ["id", "_id", "room_id"]:
            target_key = "id" if k != "_id" else "_id"
            if isinstance(v, list):
                final_filter[target_key] = {"$in": [int(i) if str(i).isdigit() else i for i in v]}
            else:
                final_filter[target_key] = int(v) if str(v).isdigit() else v
        else:
            final_filter[k] = v

    if not final_filter:
        return {"error": "Could not extract a valid query filter for deletion."}

    print(f"--- EXECUTING MONGO DELETE | Filter: {final_filter} ---")
    result = mongo.db["rooms-data"].delete_many(final_filter)
    
    return {
        "deleted_count": result.deleted_count,
        "status": "Success" if result.deleted_count > 0 else "No matching rooms found to delete"
    }

TOOLS = {
    "show_rooms": show_rooms,
    "create_rooms": create_rooms,
    "update_rooms": update_rooms,
    "delete_rooms": delete_rooms
}

def extract_action(text):
    match = re.search(r"Action:\s*([a-zA-Z_]+)", text)
    return match.group(1).strip() if match else None

def execute(self, messages):
        response = chat(model="llama3.2", messages=messages)
        result = response["message"]["content"]
        
        action = extract_action(result)
        
        if not action:
            if "update_rooms" in result: action = "update_rooms"
            elif "create_rooms" in result: action = "create_rooms"
            elif "delete_rooms" in result: action = "delete_rooms"
            elif "show_rooms" in result: action = "show_rooms"

        if action in TOOLS:
            if action == "show_rooms":
                user_query = messages[-2]["content"] if len(messages) >= 2 else "show all rooms"
                observation = show_rooms(query=user_query)

def extract_action_input(text):
    input_marker = text.find("Action Input:")
    if input_marker == -1:
        input_marker = 0
        
    sub_text = text[input_marker:]
    start_idx = sub_text.find("[") if sub_text.find("[") != -1 and sub_text.find("[") < sub_text.find("{") else sub_text.find("{")
    end_idx = sub_text.rfind("]") if sub_text.rfind("]") != -1 and sub_text.rfind("]") > sub_text.rfind("}") else sub_text.rfind("}")
    
    if start_idx != -1 and end_idx != -1:
        json_string = sub_text[start_idx:end_idx+1].strip()
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            print(f"Malforming detected, attempting regex auto-repair on: {json_string}")
            
            fixed_string = re.sub(r'\}\s*([\x22\x27])', r'},\1', json_string)
            fixed_string = re.sub(r'\}\s*\{', r'}, {', fixed_string)
            
            try:
                return json.loads(fixed_string)
            except Exception as e:
                print(f"Failed to auto-repair JSON string. Error: {str(e)}")
                return {}
    return {}