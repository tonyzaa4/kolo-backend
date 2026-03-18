from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# --- МОДЕЛІ ---
class UserRegister(BaseModel):
    email: str
    password: str

class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    language: str = "uk"

# --- МАРШРУТИ З ПРОФЕСІЙНОЮ ДОКУМЕНТАЦІЄЮ ---

@router.post(
    "/register", 
    summary="Реєстрація нового користувача", 
    description="Створює новий обліковий запис у системі. Приймає **email** та **пароль**. Повертає повідомлення про успішну реєстрацію (наразі працює як заглушка)."
)
def register_user(user: UserRegister):
    return {"message": "Користувач успішно зареєстрований (Mock)", "email": user.email}


@router.post(
    "/login", 
    summary="Вхід в систему (Отримання токена)", 
    description="Авторизація користувача. Використовує стандартну форму OAuth2 (приймає `username` та `password`). Повертає **JWT токен** доступу, який необхідний для роботи із захищеними маршрутами."
)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    return {"access_token": "12345abcde", "token_type": "bearer"}


@router.get(
    "/me", 
    response_model=UserPreferences,
    summary="Отримати налаштування профілю", 
    description="Повертає поточні налаштування авторизованого користувача (тема оформлення, мова, статус email-сповіщень). **Вимагає передачі Bearer токена**."
)
def get_user_profile(token: str = Depends(oauth2_scheme)):
    return UserPreferences(
        theme="dark",
        email_notifications=True,
        language="uk"
    )


@router.put(
    "/me", 
    response_model=UserPreferences,
    summary="Оновити налаштування профілю", 
    description="Дозволяє користувачу змінити свої особисті налаштування. Приймає JSON з новими даними та повертає оновлений об'єкт налаштувань. **Вимагає передачі Bearer токена**."
)
def update_user_profile(preferences: UserPreferences, token: str = Depends(oauth2_scheme)):
    return preferences