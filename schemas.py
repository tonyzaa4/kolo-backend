from pydantic import BaseModel
from typing import Optional
from datetime import date


class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


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


class UserSubscriptionCreate(BaseModel):
    subscription_id: Optional[int] = None
    custom_name: Optional[str] = None
    start_date: Optional[date] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    billing_cycle: Optional[str] = None


class UserSubscriptionOut(BaseModel):
    id: int
    user_id: int
    subscription_id: Optional[int]
    custom_name: Optional[str]
    start_date: Optional[date]
    price: Optional[float]
    currency: Optional[str]
    billing_cycle: Optional[str]
    status: str

    class Config:
        from_attributes = True
