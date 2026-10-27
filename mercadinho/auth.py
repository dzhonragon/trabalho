"""Autenticação e encerramento de sessão."""
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db
from .views import bp, login_required


@bp.route("/login", methods=("GET", "POST"))
def login():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, username, password_hash FROM users WHERE username = ? COLLATE NOCASE",
            (username,),
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Usuário ou senha inválidos.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            destination = request.args.get("next", "")
            # Evita redirecionamentos para domínios externos.
            if not destination.startswith("/") or destination.startswith("//"):
                destination = url_for("main.dashboard")
            return redirect(destination)

    return render_template("login.html")


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Você saiu do sistema.", "success")
    return redirect(url_for("main.login"))
