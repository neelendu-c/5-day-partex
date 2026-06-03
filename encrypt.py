# File for testing JWT logic

import jwt
import datetime

key="testkey"
payload={"user_id":11,"username":"rooms","exp":datetime.datetime.utcnow() + datetime.timedelta(days=1)}

token=jwt.encode(payload,key,algorithm='HS256')
print(token)
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMSwidXNlcm5hbWUiOiJyb29tcyIsImV4cCI6MTc4MDQwNjkyMn0.hfz69JyDFqxk4BlmY4S2_oz51KzZIzscEoq5GnV4WTE