from sqlalchemy.orm import DeclarativeBase

from database.connection import engine


class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
