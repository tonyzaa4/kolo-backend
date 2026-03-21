from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, utils
from database import get_db

# Використовуємо префікс, який просить команда в Jira
router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)


# --- Твоя реальна реєстрація (Завдання Тетяни) ---
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Реальна реєстрація користувача в MySQL:
    1. Перевірка email.
    2. Хешування пароля через utils.py.
    3. Збереження в базу через SQLAlchemy.
    """
    # Перевірка, чи існує користувач
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Цей email вже зареєстровано"
        )

    # Хешування пароля (це те, що ми робили в utils.py)
    hashed_password = utils.hash_password(user.password)

    # Створення запису
    new_user = models.User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --- Заглушка для входу (Тут буде працювати Влад) ---
@router.post("/login")
def login_user(user: schemas.UserCreate):  # Тимчасово використовуємо ту саму схему
    """
    Цей ендпоінт поки що є заглушкою (Mock).
    Влад додасть сюди логіку перевірки пароля та JWT-токени.
    """
    return {
        "token": "12345abcde-mock-token",
        "message": "Успішний вхід (Заглушка для розробки мобілки)"
    }