from datetime import datetime

from sqlalchemy import Integer, ForeignKey, Float, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database.orm import Base


class HealthRiskPrediction(Base):
    __tablename__ = "health_risk_prediction"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    diabetes_probability: Mapped[float] = mapped_column(Float)
    hypertension_probability: Mapped[float] = mapped_column(Float)

    model_version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
