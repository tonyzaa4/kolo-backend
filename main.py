from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from routers import users
from database import engine
import models

# ТИМЧАСОВО ВИМКНЕНО (Таня забула залити файли)
# from logger import setup_logging
# from app.exceptions import (
#     http_exception_handler,
#     not_found_handler,
#     validation_exception_handler
# )

# Запускаємо логування (ТИМЧАСОВО ВИМКНЕНО)
# setup_logging()

# Створюємо таблиці, якщо їх немає (про всяк випадок)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kolo API")

# Підключаємо exception handlers (ТИМЧАСОВО ВИМКНЕНО)
# app.add_exception_handler(HTTPException, http_exception_handler)
# app.add_exception_handler(404, not_found_handler)
# app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Підключаємо роутери
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Kolo API is running. Бекенд успішно запущено!"}