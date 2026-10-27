from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from mercadinho import create_app
from mercadinho.db import get_db, init_db


@pytest.fixture()
def app(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key-only",
            "DATABASE": str(tmp_path / "test.sqlite"),
            "WTF_CSRF_ENABLED": False,
            "SESSION_COOKIE_SECURE": False,
        }
    )
    with app.app_context():
        init_db()
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("operador", generate_password_hash("Senha-teste-123")),
        )
        db.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client):
    return client.post(
        "/login", data={"username": "operador", "password": "Senha-teste-123"}, follow_redirects=True
    )


@pytest.fixture()
def authenticated_client(client):
    login(client)
    return client


def add_product(app, *, name="Arroz 5 kg", code="P001", price=27.90, quantity=20, minimum_stock=5):
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            "INSERT INTO products (name, code, price, quantity, minimum_stock) VALUES (?, ?, ?, ?, ?)",
            (name, code, price, quantity, minimum_stock),
        )
        db.commit()
        return cursor.lastrowid
