from datetime import datetime

from database.orm import Base

from sqlalchemy import Integer, String, DateTime, func, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        String(256), unique=True
    )
    password_hash: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

class UserHealthProfile(Base):
    __tablename__ = "user_health_profile"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True)

    age: Mapped[int] = mapped_column(Integer)
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    smoking: Mapped[bool] = mapped_column(Boolean)
    exercise_per_week: Mapped[int] = mapped_column(Integer)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
