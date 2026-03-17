from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, utils

# Екземпляр FastAPI
app = FastAPI(title="Kolo API")


# Функція, яка відкриває зв'язок з БД на кожен запит і закриває після
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Kolo API is running"}


# --- НОВИЙ ЕНДПОІНТ РЕЄСТРАЦІЇ ---
@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Пошук в базі, чи вже є хтось із таким email
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цей email вже зареєстровано")

    # 2. Хешування паролю
    hashed_pwd = utils.hash_password(user.password)

    # 3. Створення об'єкт нового користувача
    new_user = models.User(email=user.email, hashed_password=hashed_pwd)

    # 4. Збереження в базу даних
    db.add(new_user)
    db.commit()  # Фіксація змін (зберігаємо)
    db.refresh(new_user)  # Оновлення, щоб отримати згенерований ID від MySQL

    # Повернення користувача (FastAPI сам обріже пароль завдяки response_model=schemas.UserOut)
    return new_user