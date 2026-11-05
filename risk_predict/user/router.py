from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from database.connection import get_session
from user.auth import hash_password, verify_password, create_access_token, verify_user
from user.model import User, UserHealthProfile
from user.request import SignUpRequest, LogInRequest, CreateHealthProfileRequest
from user.response import SignUpResponse, LogInResponse, UserHealthProfileResponse


router = APIRouter(tags=["User"])

@router.post(
    "/users",
    summary="회원가입 API",
    status_code=201,
    response_model=SignUpResponse,
)
async def sign_up_handler(
    body: SignUpRequest,
    session = Depends(get_session),
):
    # [1] Email 중복 검사
    stmt = select(User).where(User.email == body.email)
    result = await session.execute(stmt)
    user = result.scalar()
    if user:
        raise HTTPException(
            status_code=409, 
            detail="이미 가입된 이메일입니다."
        )

    # [2] 비밀번호 해싱
    password_hash = hash_password(plain_password=body.password)

    # [3] 회원 데이터 저장
    new_user = User(email=body.email, password_hash=password_hash)
    session.add(new_user)
    await session.commit()
    
    return new_user


@router.post(
    "/users/login",
    summary="로그인 API",
    response_model=LogInResponse,
)
async def login_handler(
    body: LogInRequest,
    session = Depends(get_session),
):
    # [1] email로 사용자 조회(회원가입 여부 확인)
    stmt = select(User).where(User.email == body.email)
    result = await session.execute(stmt)
    user = result.scalar()
    if not user:
        raise HTTPException(
            status_code=401, detail="이메일과 비밀번호가 잘못 되었습니다."
        )

    # [2] 비밀번호 검증(body.password <> user.password_hash)
    is_verified = verify_password(
        plain_password=body.password, password_hash=user.password_hash
    )
    if not is_verified:
        raise HTTPException(
            status_code=401, detail="이메일과 비밀번호가 잘못 되었습니다."
        )

    # [3] 임시 토큰(JWT) 발급
    access_token: str = create_access_token(user_id=user.id)
    return {
        "access_token": access_token
    }

@router.post(
    "/health-profiles",
    summary="건강 프로필 생성 API",
    status_code=201,
    response_model=UserHealthProfileResponse,
)
async def create_user_health_profile_handler(
    body: CreateHealthProfileRequest,
    session = Depends(get_session),
    user_id = Depends(verify_user),  # 헤더에 JWT 토큰 요구하도록 명시
):
    # [1] 프로필 중복 검사
    stmt = (
        select(UserHealthProfile)
        .where(UserHealthProfile.user_id == user_id)
    )
    result = await session.execute(stmt)
    profile = result.scalar()
    if profile:
        raise HTTPException(
            status_code=409, detail="이미 건강 프로필이 존재합니다."
        )

    # [2]
    profile_data = body.model_dump()
    new_profile = UserHealthProfile(user_id=user_id, **profile_data)
    session.add(new_profile)
    await session.commit()

    return new_profile
