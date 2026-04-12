# kolo-backend

Серверна частина застосунку **Kolo** для керування підписками.

## Швидкий запуск

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

## Що додано в цій версії

- GET автотест приватності: користувач бачить тільки власні підписки
- POST автотести створення: кастомна і каталожна підписка, перевірка `201 Created`
- `seed.py` тепер створює тестових користувачів і автоматично прив'язує кілька підписок до них
