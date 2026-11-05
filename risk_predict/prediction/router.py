from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import select
from typing import Literal

from database.connection import get_session
from user.auth import verify_user
from user.model import UserHealthProfile
from prediction.llm import predict_health_risk
from prediction.model import HealthRiskPrediction
from prediction.response import HealthRiskPredictionResponse


router = APIRouter(tags=["Prediction"])

@router.post(
    "/predictions",
    summary="건강 위험도 예측 API",
    status_code=201,
    response_model=HealthRiskPredictionResponse,
)
async def predict_health_risk_handler(
    model_version: Literal[
        "gpt-5-mini", "gpt-6-luna"
    ] = Body("gpt-5-mini", embed=True),
    session = Depends(get_session),
    # 인증 API로 변경(= 유효한 JWT 토큰을 헤더로 보내는 사용자만 요청 허용)
    user_id = Depends(verify_user),
):  
    # [1] 건강 프로필 조회
    stmt = (
        select(UserHealthProfile)
        .where(UserHealthProfile.user_id == user_id)
    )
    result = await session.execute(stmt)
    profile = result.scalar()
    if not profile:
        raise HTTPException(
            status_code=404, detail="건강 프로필이 존재하지 않습니다."
        )

    # [1a] 지난 24시간 내에 예측이 있는지 검사
    before_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    stmt = (
        select(HealthRiskPrediction)
        .where(
            HealthRiskPrediction.user_id == user_id,
            HealthRiskPrediction.created_at >= before_24h,
        )
    )
    result = await session.execute(stmt)
    last_prediction = result.scalar()
    if last_prediction:
        raise HTTPException(
            status_code=409, detail="24시간 내에 예측한 결과가 존재합니다."
        )

    # [2] 위험도 예측(OpenAI API)
    raw_prediction = await predict_health_risk(
        profile=profile, model_version=model_version
    )

    # [3] 데이터베이스에 저장
    new_prediction = HealthRiskPrediction(
        user_id=user_id,
        diabetes_probability=raw_prediction.diabetes_probability,
        hypertension_probability=raw_prediction.hypertension_probability,
        model_version=model_version,
    )
    session.add(new_prediction)
    await session.commit()
    return new_prediction
