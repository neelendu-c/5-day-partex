def room(rooms):
    return {
        "id": str(rooms["_id"]),
        "name": rooms["name"],
        "description": rooms["description"],
        "price": rooms["price"]
    }

def all_rooms(rooms):
    return [room(r) for r in rooms]