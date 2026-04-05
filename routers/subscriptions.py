from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db
from routers.users import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])


@router.get("/", response_model=List[schemas.SubscriptionOut], summary="Отримати каталог підписок")
def get_all_subscriptions(db: Session = Depends(get_db)):
    subscriptions = db.query(models.Subscription).filter(models.Subscription.is_custom == False).all()
    return subscriptions


@router.get("/my", response_model=List[schemas.UserSubscriptionOut], summary="Отримати підписки поточного користувача")
def get_my_subscriptions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.UserSubscription)
        .filter(models.UserSubscription.user_id == current_user.id)
        .order_by(models.UserSubscription.id.asc())
        .all()
    )


@router.post("/", response_model=schemas.UserSubscriptionOut, status_code=status.HTTP_201_CREATED, summary="Додати підписку користувачу")
def create_user_subscription(
    payload: schemas.UserSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.subscription_id is None and not payload.custom_name:
        raise HTTPException(status_code=400, detail="Потрібно передати subscription_id або custom_name")

    if payload.subscription_id is not None:
        base_subscription = db.query(models.Subscription).filter(models.Subscription.id == payload.subscription_id).first()
        if not base_subscription:
            raise HTTPException(status_code=404, detail="Базову підписку не знайдено")
    else:
        base_subscription = None

    new_user_subscription = models.UserSubscription(
        user_id=current_user.id,
        subscription_id=payload.subscription_id,
        custom_name=payload.custom_name,
        start_date=payload.start_date,
        price=payload.price if payload.price is not None else (base_subscription.default_price if base_subscription else None),
        currency=payload.currency if payload.currency is not None else (base_subscription.default_currency if base_subscription else None),
        billing_cycle=payload.billing_cycle,
        status="active",
    )

    db.add(new_user_subscription)
    db.commit()
    db.refresh(new_user_subscription)
    return new_user_subscription
