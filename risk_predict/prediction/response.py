from datetime import datetime

from pydantic import BaseModel


class HealthRiskPredictionResponse(BaseModel):
    id: int
    user_id: int
    diabetes_probability: float
    hypertension_probability: float
    model_version: str
    created_at: datetime
