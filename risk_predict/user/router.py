from fastapi import APIRouter


router = APIRouter()

@router.post(
    "/users",
    summary="회원가입 API",
)
async def sign_up_handler():
    return
