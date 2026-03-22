from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_404_NOT_FOUND

app = FastAPI()

# --- Обробка HTTPException (наприклад 400, 404) ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# --- Обробка 404 окремо (якщо маршрут не знайдено) ---
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={"error": "Not Found"}
    )

# --- Обробка помилок валідації (422 → зробимо 400) ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request data"}
    )

# --- Приклад роутів ---
@app.get("/")
def read_root():
    return {"message": "OK"}

@app.get("/item/{item_id}")
def get_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=400, detail="Invalid ID")
    return {"item_id": item_id}
