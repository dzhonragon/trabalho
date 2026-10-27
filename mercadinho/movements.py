"""Registro de entradas/saídas e consulta de histórico."""
from flask import abort, flash, redirect, render_template, request, url_for
import sqlite3

from .db import get_db
from .views import bp, login_required, positive_integer


@bp.route("/movimentacoes/nova", methods=("GET", "POST"))
@login_required
def new_movement():
    db = get_db()
    products = db.execute("SELECT id, name, code, quantity FROM products ORDER BY name COLLATE NOCASE").fetchall()

    if request.method == "POST":
        raw_product_id = request.form.get("product_id", "")
        movement_type = request.form.get("type", "")
        raw_quantity = request.form.get("quantity", "")
        try:
            product_id = positive_integer(raw_product_id, "O produto", allow_zero=False)
            quantity = positive_integer(raw_quantity, "A quantidade")
        except ValueError as error:
            flash(str(error), "error")
            return render_template("movement_form.html", products=products, form=request.form), 400

        if movement_type not in ("entrada", "saida"):
            flash("Selecione entrada ou saída.", "error")
            return render_template("movement_form.html", products=products, form=request.form), 400

        try:
            # BEGIN IMMEDIATE evita duas saídas concorrentes validarem o mesmo saldo.
            db.execute("BEGIN IMMEDIATE")
            product = db.execute(
                "SELECT id, name, quantity FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            if product is None:
                db.rollback()
                flash("O produto selecionado não existe.", "error")
                return render_template("movement_form.html", products=products, form=request.form), 400

            if movement_type == "saida" and quantity > product["quantity"]:
                db.rollback()
                flash(
                    f"Saída não registrada: há apenas {product['quantity']} unidade(s) disponíveis.",
                    "error",
                )
                return render_template("movement_form.html", products=products, form=request.form), 400

            delta = quantity if movement_type == "entrada" else -quantity
            db.execute(
                "INSERT INTO movements (product_id, type, quantity) VALUES (?, ?, ?)",
                (product_id, movement_type, quantity),
            )
            db.execute(
                "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                (delta, product_id),
            )
            db.commit()
        except sqlite3.Error:
            db.rollback()
            flash("Não foi possível registrar a movimentação. Nenhum saldo foi alterado.", "error")
            return render_template("movement_form.html", products=products, form=request.form), 500

        updated = db.execute("SELECT quantity, minimum_stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if updated["quantity"] <= updated["minimum_stock"]:
            flash(
                f"Movimentação registrada. Atenção: o produto está com estoque baixo ({updated['quantity']} unidade(s)).",
                "warning",
            )
        else:
            flash("Movimentação registrada e saldo atualizado.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("movement_form.html", products=products, form={})


@bp.route("/movimentacoes")
@login_required
def movement_history():
    db = get_db()
    product_id = request.args.get("product_id", "").strip()
    products = db.execute("SELECT id, name, code FROM products ORDER BY name COLLATE NOCASE").fetchall()

    sql = """SELECT m.id, m.type, m.quantity, m.created_at,
                    p.name AS product_name, p.code AS product_code
             FROM movements m JOIN products p ON p.id = m.product_id"""
    params: tuple = ()
    if product_id:
        try:
            validated_product_id = int(product_id)
            if validated_product_id <= 0:
                raise ValueError
        except ValueError:
            abort(400, description="Filtro de produto inválido.")
        sql += " WHERE m.product_id = ?"
        params = (validated_product_id,)
    sql += " ORDER BY m.created_at DESC, m.id DESC LIMIT 500"
    movements = db.execute(sql, params).fetchall()
    return render_template(
        "history.html", movements=movements, products=products, selected_product=product_id
    )
