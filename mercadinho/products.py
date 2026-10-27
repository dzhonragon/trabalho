"""Cadastro e consulta de produtos."""
import sqlite3
from decimal import Decimal, InvalidOperation

from flask import flash, redirect, render_template, request, url_for

from .db import get_db
from .views import bp, login_required, positive_integer


@bp.route("/")
@login_required
def dashboard():
    db = get_db()
    search = request.args.get("q", "").strip()[:100]
    if search:
        like_term = f"%{search}%"
        products = db.execute(
            """SELECT * FROM products
               WHERE name LIKE ? OR code LIKE ?
               ORDER BY name COLLATE NOCASE""",
            (like_term, like_term),
        ).fetchall()
    else:
        products = db.execute("SELECT * FROM products ORDER BY name COLLATE NOCASE").fetchall()

    low_stock_count = db.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= minimum_stock"
    ).fetchone()[0]
    return render_template(
        "dashboard.html", products=products, search=search, low_stock_count=low_stock_count
    )


@bp.route("/produtos/novo", methods=("GET", "POST"))
@login_required
def new_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        raw_price = request.form.get("price", "").strip().replace(",", ".")
        raw_quantity = request.form.get("quantity", "").strip()
        raw_minimum = request.form.get("minimum_stock", "").strip()
        errors: list[str] = []

        if not name:
            errors.append("Informe o nome do produto.")
        elif len(name) > 120:
            errors.append("O nome deve ter no máximo 120 caracteres.")
        if not code:
            errors.append("Informe o código do produto.")
        elif len(code) > 40:
            errors.append("O código deve ter no máximo 40 caracteres.")

        try:
            price = Decimal(raw_price)
            if not price.is_finite() or price <= 0 or price.as_tuple().exponent < -2:
                raise ValueError
        except (InvalidOperation, ValueError):
            price = Decimal("0")
            errors.append("O preço deve ser maior que zero e ter no máximo duas casas decimais.")

        try:
            quantity = positive_integer(raw_quantity, "A quantidade inicial", allow_zero=True)
        except ValueError as error:
            quantity = 0
            errors.append(str(error))
        try:
            minimum_stock = positive_integer(raw_minimum, "O estoque mínimo", allow_zero=True)
        except ValueError as error:
            minimum_stock = 0
            errors.append(str(error))

        if errors:
            for message in errors:
                flash(message, "error")
            return render_template("product_form.html", form=request.form), 400

        db = get_db()
        try:
            db.execute(
                """INSERT INTO products (name, code, price, quantity, minimum_stock)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, code, float(price), quantity, minimum_stock),
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            flash("Já existe um produto com esse código. Informe um código único.", "error")
            return render_template("product_form.html", form=request.form), 400

        flash("Produto cadastrado com sucesso.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("product_form.html", form={})
