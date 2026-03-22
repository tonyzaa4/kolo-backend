from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from database import get_db
import models
import schemas
import utils

# --- Logger ---
logger = logging.getLogger(__name__)

# --- Роутер ---
router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


# --- Модель профілю ---
class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"


# --- Реєстрація користувача ---
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    summary="Реєстрація нового користувача"
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Цей email вже зареєстровано"
            )

        hashed_password = utils.hash_password(user.password)
        new_user = models.User(email=user.email, hashed_password=hashed_password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"New user registered: {new_user.email}")
        return new_user

    except Exception as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# --- Вхід користувача ---
@router.post("/login", summary="Вхід в систему (отримання токена)")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {form_data.username}")
    # Тут поки mock токен
    return {"access_token": "12345abcde-mock", "token_type": "bearer"}


# --- Отримати налаштування профілю ---
@router.get("/me", response_model=UserPreferences, summary="Отримати налаштування профілю")
def get_user_profile(token: str = Depends(oauth2_scheme)):
    logger.info("Profile viewed")
    return UserPreferences()


# --- Оновити налаштування профілю ---
@router.put("/me", response_model=UserPreferences, summary="Оновити налаштування профілю")
def update_user_profile(preferences: UserPreferences, token: str = Depends(oauth2_scheme)):
    logger.info(f"Profile updated: {preferences.dict()}")
    return preferences
