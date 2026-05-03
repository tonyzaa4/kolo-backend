from datetime import date, timedelta
from database import SessionLocal
import models
import logging
from push_service import send_push

# Налаштовуємо логер для цього файлу
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def check_upcoming_payments():
    db = SessionLocal()
    try:
        logger.info("🔍 Запуск щоранкової перевірки підписок...")
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Дістаємо всі підписки користувачів з бази
        subscriptions = db.query(models.UserSubscription).all()
        
        for sub in subscriptions:
            # Пропускаємо, якщо немає дати старту
            if not getattr(sub, "start_date", None):
                continue
                
            # Спрощена логіка: якщо це щомісячна підписка і день оплати - завтра
            if sub.billing_cycle == "monthly" and sub.start_date.day == tomorrow.day:
                
                # Знаходимо власника підписки
                user = db.query(models.User).filter(models.User.id == sub.user_id).first()
                
                # Якщо юзер має Firebase токен - відправляємо пуш
                if user and user.fcm_token:
                    title = "Час платити!"
                    body = f"Завтра зніметься {sub.price} {sub.currency} за {sub.custom_name}"
                    
                    send_push(user.fcm_token, title, body)
                    logger.info(f"✅ Пуш відправлено на пристрій юзера {user.email}")
                    
        logger.info("🏁 Перевірку підписок завершено.")
    except Exception as e:
        logger.error(f"❌ Помилка в кроні: {e}")
    finally:
        db.close()