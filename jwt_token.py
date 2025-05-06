from datetime import datetime,timedelta
from jose import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict):
    to_encode=data.copy()
    expiry_delta=datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp":expiry_delta})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    return encode_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")  # assuming you put user_id inside token
        if user_id is None:
            return {'status_code':401, "message":"Invalid token. User ID not found."}
        return user_id
    except jwt.ExpiredSignatureError:
        return {'status_code':401, "message":"Token has expired."}
    except jwt.InvalidTokenError:
        return {'status_code':401, "message":"Invalid token."}
