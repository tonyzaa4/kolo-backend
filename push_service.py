import firebase_admin
from firebase_admin import credentials, messaging

# УВАГА: Для роботи цього скрипта потрібен файл firebase-key.json!
# Це секретний ключ вашого проєкту Firebase.
# Поки файлу немає, ми просто готуємо функцію і ставимо "заглушку", щоб код не падав.

try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
    FIREBASE_READY = True
except FileNotFoundError:
    print("⚠️ Увага: Файл firebase-key.json не знайдено. Сповіщення поки що відправлятися не будуть.")
    FIREBASE_READY = False


def send_push(token: str, title: str, body: str):
    """
    Відправляє push-сповіщення на конкретний пристрій (телефон Сані/Даші).
    """
    if not FIREBASE_READY or not token:
        print(f"🚫 Пропуск відправки пуша (немає ключа або токена). Тема: {title}")
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        response = messaging.send(message)
        print(f"✅ Пуш успішно відправлено: {response}")
        return True
    except Exception as e:
        print(f"❌ Помилка відправки пуша: {e}")
        return False