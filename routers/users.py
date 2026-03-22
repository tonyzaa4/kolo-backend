from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

import logging

logger = logging.getLogger(__name__)

# Імпортуємо наші модулі
import models
import schemas
import utils
from database import get_db

# 1. Налаштування роутера
router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# 2. Додаткові моделі для профілю (те, що було у твоєму коді)
class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"


# --- МАРШРУТИ ---

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    summary="Реєстрація нового користувача",
    description="Перевіряє email, хешує пароль та зберігає користувача в MySQL."
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Перевірка на дублікат
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цей email вже зареєстровано"
        )

    # Хешування пароля (всередині функції!)
    hashed_password = utils.hash_password(user.password)

    # Створення запису
    new_user = models.User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    summary="Вхід в систему (Отримання токена)",
    description="Авторизація через форму OAuth2. Повертає тимчасовий токен (Mock)."
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Тут пізніше Влад додасть реальну перевірку пароля
    return {"access_token": "12345abcde-mock", "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserPreferences,
    summary="Отримати налаштування профілю"
)
def get_user_profile(token: str = Depends(oauth2_scheme)):
    # Повертаємо дефолтні налаштування (заглушка)
    return UserPreferences()


@router.put(
    "/me",
    response_model=UserPreferences,
    summary="Оновити налаштування профілю"
)
def update_user_profile(preferences: UserPreferences, token: str = Depends(oauth2_scheme)):
    # Повертаємо те, що прислав користувач
    return preferences


logger.info("User registered")
logger.warning("Suspicious request")
logger.error("Database error")