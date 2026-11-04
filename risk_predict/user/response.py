from datetime import datetime

from pydantic import BaseModel


# 회원가입 응답에서 반환할 데이터 형식
class SignUpResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

# 로그인 응답에서 반환할 데이터 형식
class LogInResponse(BaseModel):
    access_token: str
