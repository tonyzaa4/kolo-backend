from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["Users"])

# Ця магічна змінна каже FastAPI: "Ці маршрути захищені токеном!"
# Вона також автоматично додасть кнопку "Authorize" (замочок) у твою документацію
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# --- Твої старі моделі ---
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# --- НОВА МОДЕЛЬ ДЛЯ НАЛАШТУВАНЬ (SCRUM-24) ---
class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"

# --- Твої старі роути ---
@router.post("/register")
def register_user(user: UserRegister):
    return {"message": "Користувач успішно зареєстрований (Mock)", "email": user.email}

@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    # Тепер ми приймаємо стандартну форму від замочка Swagger
    # Swagger вимагає, щоб ключ називався строго "access_token"
    return {
        "access_token": "12345abcde", 
        "token_type": "bearer"
    }
# --- НОВИЙ РОУТ /me (SCRUM-24) ---
@router.get("/me", response_model=UserPreferences)
def get_user_profile(token: str = Depends(oauth2_scheme)):
    # Завдяки Depends(oauth2_scheme) сервер не пустить сюди без токена.
    # Оскільки бази даних ще немає, повертаємо фейкові налаштування.
    return UserPreferences(
        theme="dark",
        email_notifications=True,
        language="uk"
    )