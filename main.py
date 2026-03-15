from fastapi import FastAPI
from routers import users # Підключаємо наш файл з папки routers

app = FastAPI(title="Subscription Manager API")

# Реєструємо маршрути користувачів у головному додатку
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Бекенд успішно запущено!"}

# Створюємо екземпляр нашого додатку
app = FastAPI(title="Kolo API")

# Створюємо базовий маршрут (кореневу адресу "/")
@app.get("/")
def read_root():
    return {"message": "Kolo API is running"}
