# src/database.py
import os

from dotenv import load_dotenv
from src.core.base_model import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Создаем engine из переменной окружения
engine = create_engine(os.getenv('DATABASE_URL'), echo=True)

# Создаем SessionLocal для dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base для SQLAlchemy моделей
Base = declarative_base()

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
