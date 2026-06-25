import json
from ollama import chat
from sessions import SESSIONS, get_session
from tools import create_rooms, delete_rooms, update_rooms, TOOLS, extract_action, extract_action_input
from db_connection import MODEL
from vector_search import show_rooms



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
        response = chat(model="llama3.2", messages=messages)
        result = response["message"]["content"]
        
        action = extract_action(result)
        
        if not action:
            if "show_rooms" in result: action = "show_rooms"
            elif "create_rooms" in result: action = "create_rooms"
            elif "update_rooms" in result: action = "update_rooms"
            elif "delete_rooms" in result: action = "delete_rooms"

        valid_actions = ["show_rooms", "create_rooms", "update_rooms", "delete_rooms"]
        
        if action in valid_actions:
            action_input = extract_action_input(result)
            
            if action == "show_rooms":
                user_query = messages[-1]["content"] if len(messages) >= 2 else "show all rooms"
                print(user_query)
                observation = show_rooms(query=user_query)
                print(observation)
                messages.append({"role": "system", "content": f"Observation:\n{observation}"})
                
                second_response = chat(model="llama3.2", messages=messages)
                # print(second_response)
                # print(type(observation))
                # print(repr(observation))
                # print(str(observation))
                # print(messages)
                
                return observation
                
            else:
                if action in TOOLS:
                    tool_function = TOOLS[action]
                    observation = tool_function(action_input)
                else:
                    observation = {"error": f"Tool {action} not properly loaded."}

            messages.append({"role": "user", "content": f"Observation: {observation}"})
            
            second_response = chat(model="llama3.2", messages=messages)
            return second_response["message"]["content"]

        return result


SYSTEM_PROMPT = """
You are an advanced room booking assistant capable of managing a room database. 
Analyze the user's request and map it to one of the available tools.

Available tools:
- show_rooms (Use when user wants to look for, find, view, list, or search for rooms)
- create_rooms (Use to add new rooms)
- update_rooms (Use to modify existing rooms)
- delete_rooms (Use to remove rooms)

CRITICAL FORMATTING GUIDELINES:

1. If the user wants to search, list, or find rooms (e.g., "Show me the cheapest room", "find rooms under 500"):
You must reply EXACTLY in this format, with NO extra JSON block:
Thought: The user wants to find rooms based on a specific criteria.
Action: show_rooms

2. For database modifications (create, update, delete), you MUST provide an Action Input JSON:
Thought: Reason here.
Action: [tool_name]
Action Input:
{ dynamic JSON matching tool format }

TOOL SPECIFIC JSON FORMATS:
- For `create_rooms`, pass a list of room objects. Ensure you use 'id' instead of '_id'.
  Example:
  Action: create_rooms
  Action Input: [ { "id": 10, "name": "Room 10", "description": "Spacious room", "price": 8000 } ]

- For `update_rooms`, pass a single object or list with 'filter' and 'update' keys.
  Example:
  Action: update_rooms
  Action Input: { "filter": { "id": 4 }, "update": { "$set": { "price": 2000 } } }

- For `delete_rooms`, pass filtering criteria.
  Example:
  Action: delete_rooms
  Action Input: { "filter": { "id": 11 } }

GENERAL RULE: If you receive a message starting with "Observation:", do not use tools. Read the data and give a friendly, conversational answer to the user.
"""