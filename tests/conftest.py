import sys
from pathlib import Path
import pytest
from httpx import AsyncClient
from httpx import ASGITransport

# Додаємо корінь проєкту до sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from main import app

@pytest.fixture
async def client():
    # Використовуємо ASGITransport замість app=...
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
