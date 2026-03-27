from faker import Faker
from sqlalchemy.orm import sessionmaker
from database import engine
import models

# --- Створюємо сесію ---
Session = sessionmaker(bind=engine)
session = Session()

fake = Faker()

# --- Кількість фейкових користувачів ---
NUM_USERS = 10

for _ in range(NUM_USERS):
    user = models.User(
        email=fake.unique.email(),
        password=fake.password(length=10)  # просто для тесту, не хешований
    )
    session.add(user)

# --- Підтверджуємо зміни ---
session.commit()
print(f"{NUM_USERS} fake users added successfully!")

# --- Закриваємо сесію ---
session.close()
