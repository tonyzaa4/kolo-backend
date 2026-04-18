from sqlalchemy.orm import Session
import models


def calculate_user_analytics(db: Session, user_id: int):
    """
    Агрегація витрат та конвертація валют на льоту.
    """
    # 1. Дістаємо всі актуальні курси валют з бази
    rates_db = db.query(models.ExchangeRate).all()
    rates = {rate.currency: rate.rate_to_uah for rate in rates_db}
    rates["UAH"] = 1.0  # Базова валюта

    # Тимчасово ставимо цільову валюту UAH
    target_currency = "UAH"
    target_rate_to_uah = rates.get(target_currency, 1.0)

    # 2. JOIN таблиці, щоб отримати ціни та категорії одним запитом
    user_subs = (
        db.query(
            models.UserSubscription.price,
            models.UserSubscription.currency,
            models.Subscription.category
        )
        .outerjoin(models.Subscription, models.UserSubscription.subscription_id == models.Subscription.id)
        .filter(models.UserSubscription.user_id == user_id)
        .all()
    )

    total_spend = 0.0
    by_category = {}

    # 3. Конвертація "на льоту"
    for price, currency, category in user_subs:
        cat_name = category if category else "Custom"
        cur = currency if currency else "USD"
        p = price if price else 0.0

        # Переводимо в гривню, а потім у цільову валюту користувача
        price_in_uah = p * rates.get(cur, 1.0)
        final_price = price_in_uah / target_rate_to_uah

        total_spend += final_price
        # Додаємо суму до відповідної категорії
        by_category[cat_name] = by_category.get(cat_name, 0.0) + final_price

    # Красивий словник, який ідеально перетвориться в JSON
    return {
        "preferred_currency": target_currency,
        "total_spend": round(total_spend, 2),
        "by_category": {k: round(v, 2) for k, v in by_category.items()}
    }