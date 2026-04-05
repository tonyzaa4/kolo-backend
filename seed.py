from datetime import date, timedelta
from faker import Faker
from database import SessionLocal, engine
import models
import utils

models.Base.metadata.create_all(bind=engine)


def seed_database():
    session = SessionLocal()
    fake = Faker()

    try:
        users_by_email = {}

        predefined_users = [
            {"email": "testuser1@example.com", "password": "password123"},
            {"email": "testuser2@example.com", "password": "password123"},
            {"email": "demo@example.com", "password": "password123"},
        ]

        for item in predefined_users:
            user = session.query(models.User).filter(models.User.email == item["email"]).first()
            if not user:
                user = models.User(
                    email=item["email"],
                    hashed_password=utils.hash_password(item["password"]),
                )
                session.add(user)
                session.flush()
            users_by_email[item["email"]] = user

        while session.query(models.User).count() < 10:
            user = models.User(
                email=fake.unique.email(),
                hashed_password=utils.hash_password(fake.password(length=10)),
            )
            session.add(user)

        services = [
            {"name": "Netflix", "category": "Entertainment", "default_price": 14.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", "is_custom": False},
            {"name": "Spotify", "category": "Music", "default_price": 9.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg", "is_custom": False},
            {"name": "YouTube Premium", "category": "Entertainment", "default_price": 11.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/b/b8/YouTube_Logo_2017.svg", "is_custom": False},
            {"name": "ChatGPT Plus", "category": "Productivity", "default_price": 20.00, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg", "is_custom": False},
            {"name": "Telegram Premium", "category": "Communication", "default_price": 4.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg", "is_custom": False},
            {"name": "Apple Music", "category": "Music", "default_price": 10.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg", "is_custom": False},
            {"name": "Amazon Prime", "category": "Entertainment", "default_price": 14.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/f/fe/Amazon_logo_%282000%29.svg", "is_custom": False},
            {"name": "Disney+", "category": "Entertainment", "default_price": 7.99, "default_currency": "USD", "icon_url": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg", "is_custom": False},
        ]

        existing_sub_names = {sub.name for sub in session.query(models.Subscription).all()}
        for service in services:
            if service["name"] not in existing_sub_names:
                session.add(models.Subscription(**service))

        session.commit()

        catalog_subs = session.query(models.Subscription).filter(models.Subscription.is_custom == False).all()
        user_one = session.query(models.User).filter(models.User.email == "testuser1@example.com").first()
        user_two = session.query(models.User).filter(models.User.email == "testuser2@example.com").first()

        def ensure_user_subscription(user_id, subscription_id=None, custom_name=None, price=None, currency=None, billing_cycle="monthly"):
            exists_query = session.query(models.UserSubscription).filter(models.UserSubscription.user_id == user_id)
            if subscription_id is not None:
                exists_query = exists_query.filter(models.UserSubscription.subscription_id == subscription_id)
            if custom_name is not None:
                exists_query = exists_query.filter(models.UserSubscription.custom_name == custom_name)
            if exists_query.first():
                return

            session.add(models.UserSubscription(
                user_id=user_id,
                subscription_id=subscription_id,
                custom_name=custom_name,
                start_date=date.today() - timedelta(days=fake.random_int(min=5, max=120)),
                price=price,
                currency=currency,
                billing_cycle=billing_cycle,
                status="active",
            ))

        if user_one and len(catalog_subs) >= 2:
            ensure_user_subscription(user_one.id, subscription_id=catalog_subs[0].id, price=catalog_subs[0].default_price, currency=catalog_subs[0].default_currency)
            ensure_user_subscription(user_one.id, subscription_id=catalog_subs[1].id, price=catalog_subs[1].default_price, currency=catalog_subs[1].default_currency)
            ensure_user_subscription(user_one.id, custom_name="Gym Membership", price=25.0, currency="USD")

        if user_two and len(catalog_subs) >= 4:
            ensure_user_subscription(user_two.id, subscription_id=catalog_subs[2].id, price=catalog_subs[2].default_price, currency=catalog_subs[2].default_currency)
            ensure_user_subscription(user_two.id, subscription_id=catalog_subs[3].id, price=catalog_subs[3].default_price, currency=catalog_subs[3].default_currency)
            ensure_user_subscription(user_two.id, custom_name="Local Cinema Club", price=12.0, currency="USD")

        session.commit()
        print("✅ Seed завершено: користувачі, каталог та тестові прив'язки підписок створені.")
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
