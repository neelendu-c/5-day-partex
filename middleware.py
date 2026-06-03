from db_connection import app
import time
from flask import g,request
from functools import wraps
import jwt

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


key="abc"
def jwt_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        auth=request.headers.get("Authorization")
        try:
            payload=jwt.decode(auth,key,algorithms=['HS256'])
            request.user=payload
        except:
            return {"result":"Error"}
        return f(*args,**kwargs)
    return decorated