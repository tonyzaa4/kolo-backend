from fastapi import FastAPI
from routers import users 

# Створюємо єдиний екземпляр додатку (назва від команди)
app = FastAPI(title="Kolo API")

# Підключаємо твої роути (реєстрація та логін)
app.include_router(users.router)

# Базовий маршрут, щоб перевіряти, чи сервер живий
@app.get("/")
def read_root():
    return {"message": "Kolo API is running. Бекенд успішно запущено!"}