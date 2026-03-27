from pydantic import BaseModel
from typing import Optional

# --- СХЕМИ КОРИСТУВАЧІВ ---
class UserCreate(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# --- НОВІ СХЕМИ ДЛЯ КАТАЛОГУ ПІДПИСОК (Спринт 3) ---
class SubscriptionOut(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    icon_url: Optional[str] = None
    default_price: float
    default_currency: str
    is_custom: bool

    class Config:
        from_attributes = True