from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from routers import users
from database import engine
from routers import users, catalog
import models

from logger import setup_logging
from app.exceptions import (
    http_exception_handler,
    not_found_handler,
    validation_exception_handler
)

# Запускаємо логування
setup_logging()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kolo API")

# Підключаємо exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Підключаємо роутери
app.include_router(users.router)
app.include_router(catalog.router)

@app.get("/")
def read_root():
    return {"message": "Kolo API is running. Бекенд успішно запущено!"}