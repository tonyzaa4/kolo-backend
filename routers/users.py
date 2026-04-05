from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

import models
import schemas
import utils
from database import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"


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
    description="Створює новий обліковий запис у системі. Перевіряє email на дублікати, хешує пароль та зберігає користувача в базі даних."
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цей email вже зареєстровано")

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
    response_model=UserPreferences,
    summary="Отримати налаштування профілю",
    description="Повертає поточні налаштування авторизованого користувача."
)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return UserPreferences()


@router.put(
    "/me",
    response_model=UserPreferences,
    summary="Оновити налаштування профілю",
    description="Дозволяє користувачу змінити свої особисті налаштування."
)
def update_user_profile(preferences: UserPreferences, current_user: models.User = Depends(get_current_user)):
    return preferences

@router.get(
    "/me/subscriptions",
    summary="Отримати мої підписки",
    description="Повертає список підписок поточного авторизованого користувача. **Тільки для авторизованих.**"
)
def get_my_subscriptions(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Варіант 1: Якщо в models.py для User налаштовано relationship("subscriptions")
    if hasattr(current_user, "subscriptions"):
        return current_user.subscriptions
    
    # Варіант 2: Якщо у вас є окрема таблиця для куплених підписок (рокоментуй, якщо так):
    # my_subs = db.query(models.UserSubscription).filter(models.UserSubscription.user_id == current_user.id).all()
    # return my_subs
    
    # Тимчасова заглушка, щоб сервер не падав, якщо таблиці ще немає
    return []
@router.post(
    "/me/subscriptions",
    status_code=status.HTTP_201_CREATED,
    summary="Додати підписку до профілю",
    description="Прив'язує існуючий сервіс з каталогу до поточного авторизованого користувача, копіюючи базову ціну та валюту."
)
def add_subscription(
    subscription_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Перевіряємо, чи існує такий сервіс у глобальному каталозі
    catalog_item = db.query(models.Subscription).filter(models.Subscription.id == subscription_id).first()
    if not catalog_item:
        raise HTTPException(status_code=404, detail="Сервіс не знайдено в каталозі")

    # 2. Створюємо особисту підписку користувача, одразу підтягуючи дефолтні значення
    new_user_sub = models.UserSubscription(
        user_id=current_user.id,
        subscription_id=catalog_item.id,
        custom_name=catalog_item.name,             # Називаємо так само (напр., Netflix)
        price=catalog_item.default_price,          # Беремо базову ціну
        currency=catalog_item.default_currency     # Беремо базову валюту
    )
    
    db.add(new_user_sub)
    db.commit()
    db.refresh(new_user_sub)
    
    return new_user_sub
