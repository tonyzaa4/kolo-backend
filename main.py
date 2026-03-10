from fastapi import FastAPI

# Створюємо екземпляр нашого додатку
app = FastAPI(title="Kolo API")

# Створюємо базовий маршрут (кореневу адресу "/")
@app.get("/")
def read_root():
    return {"message": "Kolo API is running"}