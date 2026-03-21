from fastapi import FastAPI
from routers import users
from database import engine
import models

# Створюємо таблиці, якщо їх немає (про всяк випадок)
#models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kolo API")

# Підключаємо логіку з окремих файлів
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Kolo API is running. Бекенд успішно запущено!"}