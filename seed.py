from faker import Faker
from database import SessionLocal, engine
import models
import utils

# Створюємо таблиці, якщо їх ще немає
models.Base.metadata.create_all(bind=engine)


def seed_database():
    session = SessionLocal()
    fake = Faker()

    NUM_USERS = 10
    users_added = 0

    # Перевірка, чи є вже користувачі
    if session.query(models.User).count() == 0:
        print("Додаємо фейкових користувачів...")
        for _ in range(NUM_USERS):
            raw_password = fake.password(length=10)
            hashed_pwd = utils.hash_password(raw_password)

            user = models.User(
                email=fake.unique.email(),
                hashed_password=hashed_pwd
            )
            session.add(user)
            users_added += 1

        session.commit()
        print(f"✅ {users_added} фейкових користувачів успішно додано!")
    else:
        print("Користувачі вже існують. Пропускаємо.")


    # Перевіряємо, чи база вже не заповнена підписками
    if session.query(models.Subscription).count() == 0:
        print("Додаємо базові підписки...")
        services = [
            {"name": "Netflix", "category": "Entertainment", "default_price": 14.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
             "is_custom": False},
            {"name": "Spotify", "category": "Music", "default_price": 9.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg",
             "is_custom": False},
            {"name": "YouTube Premium", "category": "Entertainment", "default_price": 11.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg",
             "is_custom": False},
            {"name": "ChatGPT Plus", "category": "Productivity", "default_price": 20.00, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", "is_custom": False},
            {"name": "Telegram Premium", "category": "Communication", "default_price": 4.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg", "is_custom": False},
            {"name": "Apple Music", "category": "Music", "default_price": 10.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
             "is_custom": False},
            {"name": "Amazon Prime", "category": "Entertainment", "default_price": 14.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Amazon_logo_%282000%29.svg",
             "is_custom": False},
            {"name": "Disney+", "category": "Entertainment", "default_price": 7.99, "default_currency": "USD",
             "icon_url": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg", "is_custom": False}
        ]

        for s in services:
            new_sub = models.Subscription(**s)
            session.add(new_sub)

        session.commit()
        print(f"✅ Успішно додано {len(services)} базових підписок!")
    else:
        print("Підписки вже існують. Пропускаємо.")

    # --- Закриваємо сесію ---
    session.close()


if __name__ == "__main__":
    seed_database()