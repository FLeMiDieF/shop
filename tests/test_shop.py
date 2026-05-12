import json


# ── Public pages ─────────────────────────────────────────────────────────────

def test_homepage_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "ShopFlask" in r.data.decode()


def test_catalog_ok(client):
    r = client.get("/catalog")
    assert r.status_code == 200


def test_product_detail_ok(client):
    r = client.get("/product/1")
    assert r.status_code == 200


def test_product_not_found(client):
    r = client.get("/product/9999")
    assert r.status_code == 404


def test_cart_empty(client):
    r = client.get("/cart")
    assert r.status_code == 200
    assert "пуст" in r.data.decode().lower()


# ── Auth pages ────────────────────────────────────────────────────────────────

def test_login_page(client):
    r = client.get("/login")
    assert r.status_code == 200


def test_register_page(client):
    r = client.get("/register")
    assert r.status_code == 200


def test_register_and_login(client):
    r = client.post("/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
    }, follow_redirects=True)
    assert r.status_code == 200

    r = client.post("/login", data={
        "email": "test@example.com",
        "password": "secret123",
    }, follow_redirects=True)
    assert r.status_code == 200


def test_wrong_password(client):
    r = client.post("/login", data={
        "email": "test@example.com",
        "password": "wrongpass",
    }, follow_redirects=True)
    assert "Неверный" in r.data.decode()


# ── REST API ──────────────────────────────────────────────────────────────────

def test_api_products_returns_list(client):
    r = client.get("/api/products")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert isinstance(data, list)
    assert len(data) > 0


def test_api_product_detail(client):
    r = client.get("/api/products/1")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "name" in data
    assert "price" in data


def test_api_product_not_found(client):
    r = client.get("/api/products/9999")
    assert r.status_code == 404


def test_api_categories(client):
    r = client.get("/api/categories")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert isinstance(data, list)
    assert any(c["name"] == "Электроника" for c in data)


def test_api_products_filter_by_category(client):
    cats = json.loads(client.get("/api/categories").data)
    cat_id = cats[0]["id"]
    r = client.get(f"/api/products?category_id={cat_id}")
    assert r.status_code == 200
    data = json.loads(r.data)
    assert all(p["category_id"] == cat_id for p in data)


def test_api_swagger_ui(client):
    r = client.get("/api/docs/")
    assert r.status_code == 200
