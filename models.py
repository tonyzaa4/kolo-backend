from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

# Імпортуємо базовий клас з нашого файлу database.py
from database import Base

# Перелік (Enum) для циклів оплати
class BillingCycle(str, enum.Enum):
    monthly = "monthly"
    yearly = "yearly"

# Таблиця користувачів
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # Відношення (Relationships) до інших таблиць
    subscriptions = relationship("UserSubscription", back_populates="owner", cascade="all, delete")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete")

# Таблиця базових (глобальних) підписок (напр. Netflix, Spotify)
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    category = Column(String(50))
    icon_url = Column(String(255))
    default_price = Column(Float, nullable=False)
    default_currency = Column(String(10), default="USD")
    is_custom = Column(Boolean, default=False)

# Таблиця ПІДПИСОК КОРИСТУВАЧА (його особистий портфель)
class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Зв'язок з глобальною підпискою (може бути пустим, якщо користувач створив свою)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    custom_name = Column(String(100), nullable=True) # Назва для власної підписки
    start_date = Column(Date)
    price = Column(Float)
    currency = Column(String(10), default="USD")
    billing_cycle = Column(Enum(BillingCycle), default=BillingCycle.monthly)
    status = Column(String(50), default="active") # active, paused, cancelled

    # Відношення
    owner = relationship("User", back_populates="subscriptions")
    base_subscription = relationship("Subscription")

# Таблиця налаштувань профілю (пов'язана 1-до-1 з User)
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(50), default="dark")
    language = Column(String(10), default="uk")
    notify_email = Column(Boolean, default=True)
    notify_push = Column(Boolean, default=False)
    remind_days_before = Column(Integer, default=3)

    # Відношення
    user = relationship("User", back_populates="preferences")