from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/api/subscriptions",
    tags=["Subscriptions"]
)
# Повертає список усіх доступних підписок (Netflix, Spotify тощо) з бази даних
@router.get("/", response_model=List[schemas.SubscriptionOut], summary="Отримати каталог підписок")
def get_all_subscriptions(db: Session = Depends(get_db)):

    subscriptions = db.query(models.Subscription).filter(models.Subscription.is_custom == False).all()
    return subscriptions