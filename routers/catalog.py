from fastapi import APIRouter, Depends
# Імпортуємо схему авторизації з твого файлу користувачів
from routers.users import oauth2_scheme

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

@router.get(
    "/",
    summary="Отримати каталог сервісів",
    description="Повертає список доступних сервісів. **Доступно тільки для авторизованих користувачів.**"
)
def get_catalog(token: str = Depends(oauth2_scheme)):
    # Якщо користувач дійшов сюди, значить він передав правильний токен
    return {
        "message": "Успішний доступ до каталогу!",
        "services": ["Netflix", "Spotify", "YouTube Premium"]
    }
