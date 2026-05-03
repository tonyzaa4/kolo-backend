from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import models
import schemas
import utils
import analytics_logic
from database import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

class FCMTokenUpdate(BaseModel):
    fcm_token: str

class UserPreferencesUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    preferred_currency: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(user: models.User) -> str:
    return f"user-{user.id}"

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    if not token.startswith("user-"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_id = int(token.split("-", 1)[1])
    except (ValueError, IndexError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut,
    summary="Реєстрація нового користувача",
    description="Створює новий обліковий запис у системі. Перевіряє email на дублікати, хешує пароль та зберігає користувача в базі даних MySQL."
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цей email вже зареєстровано"
        )

    hashed_password = utils.hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вхід в систему (Отримання токена)",
    description="Авторизація користувача. Перевіряє email/пароль і повертає bearer token."
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний email або пароль")

    return TokenResponse(access_token=create_access_token(user))

@router.get(
    "/me",
    summary="Отримати налаштування профілю",
    description="Повертає поточні налаштування авторизованого користувача. Вимагає передачі Bearer токена."
)
def get_user_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == current_user.id).first()
    
    if not db_prefs:
        db_prefs = models.UserPreference(user_id=current_user.id)
        db.add(db_prefs)
        db.commit()
        db.refresh(db_prefs)
        
    return db_prefs

@router.patch(
    "/me/preferences",
    summary="Оновити налаштування профілю",
    description="Частково оновлює налаштування (тему, мову, улюблену валюту)."
)
def update_user_preferences(
    prefs: UserPreferencesUpdate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_prefs = db.query(models.UserPreference).filter(models.UserPreference.user_id == current_user.id).first()
    
    if not db_prefs:
        db_prefs = models.UserPreference(user_id=current_user.id)
        db.add(db_prefs)

    update_data = prefs.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prefs, key, value)

    db.commit()
    db.refresh(db_prefs)
    
    return db_prefs

@router.get(
    "/me/subscriptions",
    summary="Отримати мої підписки",
    description="Повертає список підписок поточного авторизованого користувача. Тільки для авторизованих."
)
def get_my_subscriptions(current_user: models.User = Depends(get_current_user)):
    if hasattr(current_user, "subscriptions"):
        return current_user.subscriptions
    return []

@router.post(
    "/me/subscriptions",
    status_code=status.HTTP_201_CREATED,
    summary="Додати підписку до профілю",
    description="Додає існуючий сервіс з каталогу АБО створює кастомну підписку, якщо subscription_id не передано."
)
def add_subscription(
    subscription_id: Optional[int] = None,
    custom_name: Optional[str] = None,
    custom_price: Optional[float] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if subscription_id is None:
        if not custom_name or custom_price is None:
            raise HTTPException(
                status_code=400,
                detail="Для створення власної підписки необхідно вказати custom_name та custom_price"
            )

        new_user_sub = models.UserSubscription(
            user_id=current_user.id,
            custom_name=custom_name,
            price=custom_price,
            currency="UAH"
        )

    else:
        catalog_item = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
        if not catalog_item:
            raise HTTPException(status_code=404, detail="Сервіс не знайдено в каталозі")

        new_user_sub = models.UserSubscription(
            user_id=current_user.id,
            subscription_id=catalog_item.id,
            custom_name=catalog_item.name,
            price=catalog_item.default_price,
            currency=catalog_item.default_currency
        )

    db.add(new_user_sub)
    db.commit()
    db.refresh(new_user_sub)

    return new_user_sub
@router.get(
    "/analytics",
    response_model=schemas.AnalyticsOut,
    summary="Аналітика витрат",
    description="Повертає реальну аналітику витрат користувача на основі його підписок."
)
def get_analytics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analytics_data = analytics_logic.calculate_user_analytics(current_user.id, db)
    
    return analytics_data

@router.patch(
    "/me/fcm-token",
    summary="Зберегти FCM токен пристрою",
    description="Приймає Firebase Cloud Messaging токен від мобільного додатку і зберігає його для подальшої відправки пуш-сповіщень."
)
def update_fcm_token(
    token_data: FCMTokenUpdate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Оновлюємо токен поточного юзера
    current_user.fcm_token = token_data.fcm_token
    db.commit()
    
    return {"message": "FCM токен успішно збережено!"}