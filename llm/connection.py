from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


DATABASE_URL = "sqlite+aiosqlite:///llm.db"

engine = create_async_engine(DATABASE_URL, echo=True)

SessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

async def get_session():
    session = SessionFactory()
    try:
        yield session
    finally:
        await session.close()
