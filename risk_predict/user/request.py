from pydantic import BaseModel, EmailStr


# 회원가입 요청에 필요한 요청 본문 형식
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str

# 로그인 요청에 필요한 요청 본문 형식
class LogInRequest(BaseModel):
    email: EmailStr
    password: str

# 건강 프로필 생성에 필요한 요청 본문 형식
class CreateHealthProfileRequest(BaseModel):
    age: int
    height_cm: float
    weight_kg: float
    smoking: bool
    exercise_per_week: int
