import time
from apscheduler.schedulers.background import BackgroundScheduler
from currency_updater import fetch_and_save_rates
from routers import users, catalog, currency, subscriptions
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from database import engine
from subscription_checker import check_upcoming_payments
import models
from app.logger import setup_logging
from app.exceptions import (
    http_exception_handler,
    not_found_handler,
    validation_exception_handler,
)

access_logger = setup_logging()

# --- КРАСА ДЛЯ SWAGGER ---
tags_metadata = [
    {"name": "Users", "description": "Операції з користувачами: реєстрація, авторизація, налаштування профілю та аналітика."},
    {"name": "Subscriptions", "description": "Керування особистими підписками (додавання сервісів, кастомні підписки, списки)."},
    {"name": "Catalog", "description": "Глобальний каталог популярних підписок (пошук, фільтрація за ціною та категорією)."},
    {"name": "Currency", "description": "Автоматично оновлювані курси валют від НБУ для точної конвертації витрат."}
]

app = FastAPI(
    title="Kolo API 🚀",
    description="Офіційний бекенд для мобільного додатку **Kolo - Менеджер підписок**.\n\nAPI забезпечує авторизацію, керування підписками, підрахунок аналітики витрат, фонову розсилку пуш-сповіщень та інтеграцію з курсами валют НБУ.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Kolo Developers Team",
    }
)

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()

    fetch_and_save_rates()
    scheduler.add_job(fetch_and_save_rates, 'cron', hour=0, minute=0)

    scheduler.add_job(check_upcoming_payments, 'cron', hour=9, minute=0)

    scheduler.start()

    access_logger.info("⏰ Фоновий планувальник запущено! Курси валют оновлюватимуться щодня.")

@app.middleware("http")
async def log_catalog_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)

    if request.url.path.startswith("/api/catalog"):
        process_time = round(time.time() - start_time, 4)
        client_ip = request.client.host if request.client else "unknown"

        access_logger.info(
            "%s %s | status=%s | duration=%ss | client=%s",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            client_ip,
        )

    return response

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users.router)
app.include_router(subscriptions.router)
app.include_router(catalog.router)
app.include_router(currency.router)

@app.get("/", tags=["Healthcheck"], summary="Перевірка статусу сервера")
def read_root():
    return {"message": "Kolo API is running. Бекенд успішно запущено!"} 