"""Aplicação de controle de estoque para um pequeno mercadinho."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, session
from flask_wtf.csrf import CSRFProtect

from .db import init_app as init_db_app

csrf = CSRFProtect()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    default_database = instance_path / "mercadinho.sqlite"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this-secret"),
        DATABASE=os.environ.get("DATABASE", str(default_database)),
        WTF_CSRF_ENABLED=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    init_db_app(app)
    csrf.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    @app.context_processor
    def inject_session_user():
        return {"session_username": session.get("username")}

    return app
