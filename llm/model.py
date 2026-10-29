from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from connection import engine


# 테이블을 일괄 생성하는 유틸리티 함수
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 테이블 정의에 사용하는 부모 클래스
class Base(DeclarativeBase):
    pass

class ChatRoom(Base):
    __tablename__ = "chat_room"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()  # DB 시간을 자동으로 기록
    )

class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    # 어떤 채팅방에서 진행한 대화인지
    chat_room_id: Mapped[int] = mapped_column(
        ForeignKey("chat_room.id")
    )
    role: Mapped[str] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
