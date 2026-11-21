from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from core.config import settings

engine=create_async_engine(
    settings.DATABASE_URL,
    echo=True
)

sessionlocal=async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base=declarative_base()

async def obtener_bd():
    db = sessionlocal()
    try:
        yield db
    finally:
        await db.close()