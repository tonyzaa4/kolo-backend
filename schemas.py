from pydantic import BaseModel, EmailStr
#from datetime import datetime- закоментувала, бо при розборі коду від поки не потрібен, але можливо в майбутньому буде)
from typing import Optional

# 1. Схема для отримання даних ВІД клієнта (при реєстрації)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2. Схема для відправки даних ДО клієнта (Безпечна!)
class UserOut(BaseModel):
    id: int
    email: EmailStr
    # пароля тут немає, тому він ніколи не "витікає" в інтернет

    class SubscriptionOut(BaseModel):
        id: int
        name: str
        category: Optional[str] = None
        icon_url: Optional[str] = None
        default_price: float
        default_currency: str
        is_custom: bool

        class Config:
            from_attributes = True  # Це дозволяє FastAPI читати дані прямо з бази MySQL

