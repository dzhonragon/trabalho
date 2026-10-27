"""Acesso SQLite e comandos de administração do banco."""
from __future__ import annotations

import sqlite3
import os

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db() -> sqlite3.Connection:
    """Retorna a conexão SQLite da requisição atual."""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"], timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        g.db = connection
    return g.db


def close_db(_exception: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db() -> None:
    db = get_db()
    with current_app.open_resource("schema.sql") as schema_file:
        db.executescript(schema_file.read().decode("utf-8"))
    click.echo("Banco de dados inicializado.")


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(seed_demo_command)
    app.cli.add_command(create_demo_user_command)

@click.command("init-db")
def init_db_command() -> None:
    """Cria as tabelas do sistema (sem apagar dados existentes)."""
    init_db()


@click.command("create-user")
@click.option("--username", prompt=True, help="Nome de usuário para acesso ao sistema.")
def create_user_command(username: str) -> None:
    """Cria um usuário com senha armazenada em hash."""
    username = username.strip()
    if len(username) < 3 or len(username) > 80:
        raise click.ClickException("O usuário deve ter entre 3 e 80 caracteres.")

    password = click.prompt("Senha", hide_input=True, confirmation_prompt=True)
    if len(password) < 10:
        raise click.ClickException("A senha deve possuir pelo menos 10 caracteres.")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError as error:
        db.rollback()
        raise click.ClickException("Esse nome de usuário já existe.") from error
    click.echo(f"Usuário '{username}' criado com sucesso.")


@click.command("seed-demo")
def seed_demo_command() -> None:
    """Insere três produtos fictícios para demonstração, sem duplicar códigos."""
    db = get_db()
    demo_products = [
        ("Arroz 5 kg", "P001", 27.90, 20, 5),
        ("Leite 1 L", "P002", 5.50, 3, 5),
        ("Feijão 1 kg", "P003", 8.90, 8, 4),
    ]
    inserted = 0
    for product in demo_products:
        exists = db.execute("SELECT 1 FROM products WHERE code = ? COLLATE NOCASE", (product[1],)).fetchone()
        if exists is None:
            db.execute(
                "INSERT INTO products (name, code, price, quantity, minimum_stock) VALUES (?, ?, ?, ?, ?)",
                product,
            )
            inserted += 1
    db.commit()
    click.echo(f"Produtos de demonstração adicionados: {inserted}. Dados totalmente fictícios.")

@click.command("create-demo-user")
def create_demo_user_command() -> None:
    """Cria o usuário de demonstração se ele ainda não existir."""
    username = os.environ.get("DEMO_USERNAME", "teste")
    password = os.environ.get("DEMO_PASSWORD")

    if not password:
        raise click.ClickException(
            "Configure a variável de ambiente DEMO_PASSWORD."
        )

    db = get_db()
    existing_user = db.execute(
        "SELECT 1 FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if existing_user:
        click.echo(f"O usuário '{username}' já existe; nenhuma alteração feita.")
        return

    try:
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError as error:
        db.rollback()
        raise click.ClickException(
            "Não foi possível criar o usuário de demonstração."
        ) from error

    click.echo(f"Usuário de demonstração '{username}' criado.")
