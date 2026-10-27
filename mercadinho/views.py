"""Blueprint principal e utilidades comuns das rotas."""
from functools import wraps

from flask import Blueprint, flash, redirect, request, session, url_for

from .db import get_db

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            flash("Entre com seu usuário para acessar o sistema.", "info")
            return redirect(url_for("main.login", next=request.path))
        return view(**kwargs)
    return wrapped_view


def positive_integer(raw_value: str, field_label: str, *, allow_zero: bool = False) -> int:
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_label} deve ser um número inteiro.") from error
    minimum = 0 if allow_zero else 1
    if value < minimum:
        comparison = "maior ou igual a zero" if allow_zero else "maior que zero"
        raise ValueError(f"{field_label} deve ser {comparison}.")
    return value
