from pydantic import BaseModel, EmailStr
from datetime import datetime

# 1. Схема для отримання даних ВІД клієнта (при реєстрації)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2. Схема для відправки даних ДО клієнта (Безпечна!)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    # пароля тут немає, тому він ніколи не "витікає" в інтернет

    class Config:
        from_attributes = True  # Це дозволяє схемі читати дані прямо з бази SQLAlchemy