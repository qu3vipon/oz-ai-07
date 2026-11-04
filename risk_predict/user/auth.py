from datetime import datetime, timezone, timedelta

import bcrypt
import jwt

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

from config import settings


def hash_password(plain_password: str) -> str:
    hashed_password: bytes = bcrypt.hashpw(
        plain_password.encode(), bcrypt.gensalt()
    )
    return hashed_password.decode()

def verify_password(
    plain_password: str, password_hash: str
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode(), password_hash.encode()
    )

# JWT(= JSON Web Token)
def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(
        payload=payload, 
        key=settings.jwt_secret_key, 
        algorithm="HS256",
    )

def verify_access_token(access_token: str) -> dict:
    try:
        payload = jwt.decode(
            jwt=access_token, 
            key=settings.jwt_secret_key,  # 서명 확인
            algorithms=["HS256"],
        )
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="잘못된 토큰 형식입니다.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="만료된 토큰입니다.")
    return payload

# HTTP 헤더에 인증 토큰이 있는지 검증
# auth_header = {"Authorization": "Bearer xxxx"}
def verify_user(
    auth_header = Depends(HTTPBearer())
) -> int:
    access_token = auth_header.credentials
    payload = verify_access_token(access_token=access_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="sub 값이 없습니다."
        )
    return int(user_id)
