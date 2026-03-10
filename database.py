import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Завантажуємо змінні середовища з файлу .env
load_dotenv()

# Отримуємо дані для підключення з .env
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "kolo_db")

# Формуємо URL для підключення (використовуємо pymysql драйвер)
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Створюємо двигун (engine), який відповідає за спілкування з базою
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Створюємо фабрику сесій для запитів до бази
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас, від якого будуть успадковуватися всі наші моделі (таблиці)
Base = declarative_base()

# Залежність (Dependency) для FastAPI, щоб відкривати і закривати з'єднання для кожного запиту
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()