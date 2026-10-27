from .conftest import add_product, login
from mercadinho.db import get_db


def test_private_pages_redirect_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_rejects_invalid_password(client):
    response = client.post("/login", data={"username": "operador", "password": "errada"})
    assert response.status_code == 200
    assert "Usuário ou senha inválidos" in response.get_data(as_text=True)


def test_login_success(authenticated_client):
    response = authenticated_client.get("/")
    assert response.status_code == 200
    assert "Consulta de estoque" in response.get_data(as_text=True)


def test_product_registration_and_dashboard(app, authenticated_client):
    response = authenticated_client.post(
        "/produtos/novo",
        data={"name": "Café 500 g", "code": "CAF001", "price": "14.90", "quantity": "6", "minimum_stock": "2"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Produto cadastrado com sucesso" in page
    assert "Café 500 g" in page
    with app.app_context():
        row = get_db().execute("SELECT quantity FROM products WHERE code = 'CAF001'").fetchone()
        assert row["quantity"] == 6


def test_duplicate_product_code_is_rejected(app, authenticated_client):
    add_product(app)
    response = authenticated_client.post(
        "/produtos/novo",
        data={"name": "Outro arroz", "code": "p001", "price": "10.00", "quantity": "2", "minimum_stock": "1"},
    )
    assert response.status_code == 400
    assert "código" in response.get_data(as_text=True).lower()


def test_movement_updates_balance_and_history(app, authenticated_client):
    product_id = add_product(app)
    response = authenticated_client.post(
        "/movimentacoes/nova",
        data={"product_id": str(product_id), "type": "saida", "quantity": "2"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Movimentação registrada" in response.get_data(as_text=True)
    with app.app_context():
        db = get_db()
        product = db.execute("SELECT quantity FROM products WHERE id = ?", (product_id,)).fetchone()
        movement = db.execute("SELECT type, quantity FROM movements WHERE product_id = ?", (product_id,)).fetchone()
        assert product["quantity"] == 18
        assert movement["type"] == "saida"
        assert movement["quantity"] == 2
    history = authenticated_client.get("/movimentacoes")
    assert "Arroz 5 kg" in history.get_data(as_text=True)


def test_oversized_exit_is_rejected_without_changing_stock(app, authenticated_client):
    product_id = add_product(app, quantity=3)
    response = authenticated_client.post(
        "/movimentacoes/nova",
        data={"product_id": str(product_id), "type": "saida", "quantity": "4"},
    )
    assert response.status_code == 400
    assert "Saída não registrada" in response.get_data(as_text=True)
    with app.app_context():
        db = get_db()
        product = db.execute("SELECT quantity FROM products WHERE id = ?", (product_id,)).fetchone()
        movement_count = db.execute("SELECT COUNT(*) FROM movements WHERE product_id = ?", (product_id,)).fetchone()[0]
        assert product["quantity"] == 3
        assert movement_count == 0


def test_low_stock_text_alert_is_present(app, authenticated_client):
    add_product(app, name="Leite 1 L", code="L001", quantity=3, minimum_stock=5)
    page = authenticated_client.get("/").get_data(as_text=True)
    assert "Estoque baixo" in page
    assert "Leite 1 L" in page


def test_empty_and_non_integer_quantities_are_rejected(app, authenticated_client):
    product_id = add_product(app)
    response = authenticated_client.post(
        "/movimentacoes/nova",
        data={"product_id": str(product_id), "type": "entrada", "quantity": "1.5"},
    )
    assert response.status_code == 400
    with app.app_context():
        db = get_db()
        product = db.execute("SELECT quantity FROM products WHERE id = ?", (product_id,)).fetchone()
        assert product["quantity"] == 20
