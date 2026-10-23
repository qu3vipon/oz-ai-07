# ORM의 클래스와 테이블 연결 정보
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


# 테이블 정의 부모 클래스
class Base(DeclarativeBase):
    pass

# item 테이블
class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(64))
    price: Mapped[int] = mapped_column(Integer)
