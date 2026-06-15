from db_connection import mongo, app, uri
from models import Room
from sessions import SESSIONS,get_session

from ollama import chat

import json
import re

# TOOLS
def show_all_rooms():
    rooms = []
    for room in mongo.db["rooms-data"].find({}):
        room["_id"] = str(room["_id"])
        rooms.append(room)
    return rooms

def create_room(addroom: Room):
    room={'id': addroom.id, 'name': addroom.name,'description': addroom.description,'price': addroom.price}
    mongo.db["rooms-data"].insert_one(room)
    return{"result": "Room added successfully with chatbot"}

def delete_room(addroom: Room):
    mongo.db["rooms-data"].delete_one({"id": addroom.id})
    return{"result": "Room deleted successfully with chatbot"}

def update_room(updroom: Room):

    room = {"id": updroom.id,"name": updroom.name,"description": updroom.description,"price": updroom.price}

    result = mongo.db["rooms-data"].update_one({"id": updroom.id},{"$set": room})

    return {"matched": result.matched_count,"modified": result.modified_count}

TOOLS = {
    "show_all_rooms": show_all_rooms,
    "create_room": create_room,
    "update_room": update_room,
    "delete_room": delete_room
}

def extract_action(text):

    match = re.search(r"Action:\s*([a-zA-Z_]+)",text)

    if not match:
        return None

    return match.group(1)

def extract_action_input(text):

    match = re.search(r"Action Input:\s*(\{.*\})",text,re.DOTALL)

    if not match:
        return {}

    return json.loads(match.group(1))

class RoomAgent:

    def __init__(self, system=None, tools=None):
        self.system = system
        self.tools = tools or {}

    def __call__(self, session_id, message):

        if session_id not in SESSIONS:

            SESSIONS[session_id] = []

            if self.system:
                SESSIONS[session_id].append({
                    "role": "system",
                    "content": self.system
                })

        messages = SESSIONS[session_id]

        messages.append({
            "role": "user",
            "content": message
        })

        result = self.execute(messages)

        messages.append({
            "role": "assistant",
            "content": result
        })

        return result

    def execute(self, messages):

        # print("========== MESSAGES ==========")
        # for m in messages:
        #     print(m)
        # print("=============================")

        response = chat(
            model="llama3.2",
            messages=messages
        )

        result = response["message"]["content"]

        action = extract_action(result)
        action_input = extract_action_input(result)
        # print("EXTRACTED ACTION:", action)
        # print("TOOLS:", TOOLS.keys())

        if action in TOOLS:

            # print("TOOL FOUND")

            # observation = TOOLS[action]()

            # print("OBSERVATION:")
            # print(observation)

            # self.messages.append({
            #     "role": "assistant",
            #     "content": result
            # })

            # self.messages.append({
            #     "role": "user",
            #     "content": f"Observation: {observation}"
            # })

            # print("CALLING LLM AGAIN")

            # response = chat(
            #     model="llama3.2",
            #     messages=self.messages
            # )

            # final_result = response["message"]["content"]

            # print("FINAL RESULT:")
            # print(final_result)

            # return final_result

            if action == "show_all_rooms":

                observation = show_all_rooms()

                messages.append({
                    "role": "user",
                    "content": f"Observation: {json.dumps(observation)}"
                })

                response = chat(
                    model="llama3.2",
                    messages=messages
                )

                # return response["message"]["content"]
                final_response = response["message"]["content"]

                print("FINAL RESPONSE RETURNED:")
                print(final_response)

                return final_response

            elif action == "create_room":

                room = Room(
                    id=action_input["id"],
                    name=action_input["name"],
                    description=action_input["description"],
                    price=action_input["price"]
                )

                observation = create_room(room)

                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })

                response = chat(model="llama3.2",messages=messages)

                return response["message"]["content"]

            elif action == "update_room":

                room = Room(id=action_input["id"],name=action_input["name"],description=action_input["description"],price=action_input["price"])

                observation = update_room(room)

                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })

                response = chat(model="llama3.2",messages=messages)


                return response["message"]["content"]
            
            elif action == "delete_room":

                room = Room(id=action_input["id"],name=action_input["name"],description=action_input["description"],price=action_input["price"])

                observation = delete_room(room)

                messages.append({
                    "role": "user",
                    "content": f"Observation: {observation}"
                })

                response = chat(model="llama3.2",messages=messages)


                return response["message"]["content"]

        return result



SYSTEM_PROMPT = """
You are a room booking assistant.

Available tools:
- show_all_rooms
- create_room
- update_room
- delete_room

When using show_all_rooms, respond EXACTLY:

Thought: reason

Action: show_all_rooms

Wait for Observation.

After receiving Observation:

Final Answer: answer



If user prompt is not enough to extrapolate ALL fields, then KEEP REQUIRED FIELDS EMPTY. When using create_room, update_room or delete_room, respond in EXACTLY THE FOLLOWING FORMAT:

Thought: reason

Action: create_room OR update_room OR delete_room

Action Input:
{
  "id": ,
  "name": "",
  "description": "",
  "price": 
}

Wait for Observation.

After receiving Observation:

Final Answer: answer

IF the user's prompt does not include any of the above tools, reply as normal.
"""



# testing code
# agent = RoomAgent(SYSTEM_PROMPT)

# result = agent("session id","Can you update room ID 8 to have name Room 7 and description 'Bigger room' with a price 9100")
# print(result)
# # result = agent("session id","Can you delete room with ID 8")
# result = agent("session id","Can you show all rooms")
# # # result = agent("Can you create ID 9 with name Room 7 and description 'Smallest room' with price 1800")

# print(result)