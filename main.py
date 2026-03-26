import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from database import engine
from routers import users, catalog
import models

from app.logger import setup_logging
from app.exceptions import (
    http_exception_handler,
    not_found_handler,
    validation_exception_handler,
)

# Запускаємо логування
access_logger = setup_logging()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kolo API")


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
