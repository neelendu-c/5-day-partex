from pydantic import BaseModel, Field

class Room(BaseModel):
    """Details of a room in the hotel"""
    id: int = Field(description="The ID of the room")
    name: str = Field(description="The name of the room")
    description: str = Field(description="The description of the room with any additional details included")
    price: float = Field(description="The price of the room")

class ChatProduct(BaseModel):
    operation: str = Field(description="The operation user wants to perform. You only have four choices - show, insert, update, delete")
    details: Room = Field(description="The details of the room")
    
# CHAT CLASSES

class ChatRequest(BaseModel):
    session_id:str
    message: str

class ChatRespond(BaseModel):
    success: bool
    response: str