from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Імпортуємо наші модулі
import models
import schemas
import utils
from database import get_db

# 1. Налаштування роутера
router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# 2. Додаткові моделі для профілю
class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"


# --- МАРШРУТИ З ДОКУМЕНТАЦІЄЮ ТА БАЗОЮ ДАНИХ ---

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    summary="Реєстрація нового користувача",
    description="Створює новий обліковий запис у системі. Перевіряє email на дублікати, хешує пароль та **зберігає користувача в базі даних MySQL**."
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Перевірка на дублікат
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цей email вже зареєстровано"
        )

    # Хешування пароля
    hashed_password = utils.hash_password(user.password)

    # Створення запису в базі
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    summary="Вхід в систему (Отримання токена)",
    description="Авторизація користувача. Використовує стандартну форму OAuth2 (приймає `username` та `password`). Повертає **JWT токен** доступу."
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Тут пізніше додамо реальну перевірку пароля в базі
    return {"access_token": "12345abcde-mock", "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserPreferences,
    summary="Отримати налаштування профілю",
    description="Повертає поточні налаштування авторизованого користувача (тема оформлення, мова, статус email-сповіщень). **Вимагає передачі Bearer токена**."
)
def get_user_profile(token: str = Depends(oauth2_scheme)):
    # Повертаємо дефолтні налаштування (заглушка)
    return UserPreferences()


@router.put(
    "/me",
    response_model=UserPreferences,
    summary="Оновити налаштування профілю",
    description="Дозволяє користувачу змінити свої особисті налаштування. Приймає JSON з новими даними та повертає оновлений об'єкт налаштувань. **Вимагає передачі Bearer токена**."
)
def update_user_profile(preferences: UserPreferences, token: str = Depends(oauth2_scheme)):
    # Повертаємо те, що прислав користувач
    return preferences