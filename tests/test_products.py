"""Tests del contrato de la API de productos.

Este archivo es IDÉNTICO en las etapas 1, 2 y 3. Es la idea central del ejercicio:
la estructura interna cambia (memoria → base de datos → capas), pero el contrato
público de la API no, y los tests lo demuestran.
"""
API = "/api/v1/products"
POLO = {"sku": "POLO-001", "name": "Polo básico", "price": "39.90", "stock": 50}


def create(client, **overrides):
    r = client.post(API, json={**POLO, **overrides})
    assert r.status_code == 201, r.text
    return r.json()


# ---------- Crear ----------
def test_create_returns_201_and_location(client):
    r = client.post(API, json=POLO)
    assert r.status_code == 201
    body = r.json()
    assert body["sku"] == "POLO-001"
    assert body["price"] == "39.90"          # el dinero viaja como texto exacto, no float
    assert body["is_active"] is True
    assert r.headers["location"] == f"{API}/{body['id']}"


def test_duplicate_sku_returns_409(client):
    create(client)
    assert client.post(API, json=POLO).status_code == 409


def test_invalid_data_is_rejected(client):
    for bad in ({"sku": "polo 1"}, {"price": "0"}, {"price": "1.999"}, {"stock": -1}, {"name": ""}):
        r = client.post(API, json={**POLO, **bad})
        assert r.status_code in (400, 422), bad


# ---------- Leer ----------
def test_get_one_and_404(client):
    product = create(client)
    assert client.get(f"{API}/{product['id']}").json()["name"] == "Polo básico"
    assert client.get(f"{API}/999").status_code == 404


def test_list_is_paginated(client):
    for i in range(5):
        create(client, sku=f"SKU-{i}")
    body = client.get(API, params={"page": 2, "size": 2}).json()
    assert body["total"] == 5
    assert body["pages"] == 3
    assert body["page"] == 2
    assert len(body["items"]) == 2


def test_list_filters(client):
    create(client, sku="POLO-001", name="Polo básico", price="39.90", stock=10)
    create(client, sku="POLO-002", name="Polo deportivo", price="59.90", stock=0)
    create(client, sku="TAZA-001", name="Taza térmica", price="25.50", stock=5)

    def skus(**params):
        return [p["sku"] for p in client.get(API, params=params).json()["items"]]

    assert set(skus(search="polo")) == {"POLO-001", "POLO-002"}
    assert set(skus(in_stock="true")) == {"POLO-001", "TAZA-001"}
    assert set(skus(min_price="30", max_price="50")) == {"POLO-001"}


def test_list_sorting(client):
    create(client, sku="A-1", price="50.00")
    create(client, sku="B-1", price="10.00")
    create(client, sku="C-1", price="30.00")

    prices = [p["price"] for p in client.get(API, params={"sort": "price"}).json()["items"]]
    assert prices == ["10.00", "30.00", "50.00"]
    prices = [p["price"] for p in client.get(API, params={"sort": "-price"}).json()["items"]]
    assert prices == ["50.00", "30.00", "10.00"]


def test_invalid_sort_field_is_rejected(client):
    assert client.get(API, params={"sort": "stock"}).status_code in (400, 422)


# ---------- Modificar ----------
def test_patch_changes_only_sent_fields(client):
    product = create(client)
    r = client.patch(f"{API}/{product['id']}", json={"price": "35.00"})
    assert r.status_code == 200
    assert r.json()["price"] == "35.00"
    assert r.json()["stock"] == 50           # no se perdió


def test_patch_missing_returns_404(client):
    assert client.patch(f"{API}/999", json={"price": "1.00"}).status_code == 404


# ---------- Borrar ----------
def test_delete_returns_204_then_404(client):
    product = create(client)
    assert client.delete(f"{API}/{product['id']}").status_code == 204
    assert client.get(f"{API}/{product['id']}").status_code == 404
    assert client.delete(f"{API}/{product['id']}").status_code == 404
