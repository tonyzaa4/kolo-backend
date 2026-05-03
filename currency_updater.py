import requests
import logging
from database import SessionLocal
from models import ExchangeRate

# Налаштовуємо логер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Додаємо вивід у консоль для прямого запуску файлу
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

def fetch_and_save_rates():
    db = SessionLocal()

    try:
        logger.info("🌐 Звертаємось до API НБУ...")
        # запит до Національного банку
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        response = requests.get(url)
        data = response.json()

        # Збереження в базу
        target_currencies = ["USD", "EUR"]

        for item in data:
            currency_code = item.get("cc")

            if currency_code in target_currencies:
                rate = item.get("rate")

                # Перевірка, чи є вже така валюта у нашій БД
                db_rate = db.query(ExchangeRate).filter(ExchangeRate.currency == currency_code).first()

                if db_rate:
                    # Якщо валюта вже є - оновлення курсу на сьогоднішній
                    db_rate.rate_to_uah = rate
                    logger.info(f"🔄 Оновлено курс: {currency_code} = {rate} ₴")
                else:
                    # Якщо валюти ще немає (перший запуск) - створення
                    new_rate = ExchangeRate(currency=currency_code, rate_to_uah=rate)
                    db.add(new_rate)
                    logger.info(f"✅ Додано новий курс: {currency_code} = {rate} ₴")

        db.commit()
        logger.info("🎉 Успіх! Всі актуальні курси збережено в базу.")

    except Exception as e:
        logger.error(f"❌ Виникла помилка: {e}")

    finally:
        db.close()

# Цей блок запускає функцію, якщо просто запускається цей файл!!!
if __name__ == "__main__":
    fetch_and_save_rates()