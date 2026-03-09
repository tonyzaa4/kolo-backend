from fastapi import FastAPI
from routers import users # Підключаємо наш файл з папки routers

app = FastAPI(title="Subscription Manager API")

# Реєструємо маршрути користувачів у головному додатку
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Бекенд успішно запущено!"}
