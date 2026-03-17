from fastapi import APIRouter
from pydantic import BaseModel

# Додаємо префікс /api/users, щоб ідеально відповідати завданню в Jira
router = APIRouter(prefix="/api/users", tags=["Users"])

# 1. Створюємо моделі для прийому JSON
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# 2. Пишемо наші Mocks (заглушки)
@router.post("/register")
def register_user(user: UserRegister):
    # Тут поки немає бази даних, тому просто повертаємо успіх
    return {
        "message": "Користувач успішно зареєстрований (Mock)", 
        "email": user.email
    }

@router.post("/login")
def login_user(user: UserLogin):
    # Повертаємо фейковий токен, як просять у завданні
    return {
        "token": "12345abcde", 
        "message": "Успішний вхід (Mock)"
    }

# Твої попередні GET-роути можуть залишатися нижче...