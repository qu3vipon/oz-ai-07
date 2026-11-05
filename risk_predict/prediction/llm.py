from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from user.model import UserHealthProfile
from config import settings


client = AsyncOpenAI(api_key=settings.openai_api_key)

class RiskPredictionResult(BaseModel):
    diabetes_probability: float = Field(..., description="당뇨 위험도")
    hypertension_probability: float = Field(..., description="고혈압 위험도")

async def predict_health_risk(
    profile: UserHealthProfile, model_version: str
) -> RiskPredictionResult:
    prompt = f"""
    다음 건강 정보를 기반으로 당뇨와 고혈압 위험도를 0과 1 사이로 계산하라.

    age: {profile.age}
    height_cm: {profile.height_cm}
    weight_kg: {profile.weight_kg}
    smoking: {profile.smoking}
    exercise_per_week: {profile.exercise_per_week}
    """

    response = await client.responses.parse(
        model=model_version,
        input=prompt,
        text_format=RiskPredictionResult,
    )
    return response.output_parsed
