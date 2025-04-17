from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base
from dotenv import load_dotenv
import os
load_dotenv()

# Создание движка SQLAlchemy
engine = create_async_engine(os.environ.get("DATABASE_URL"))


# Фабрика сессий
async_session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

# Получение сессии
async def get_async_db():
  async with async_session_maker() as session:
    yield session

# Функция для создания таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)