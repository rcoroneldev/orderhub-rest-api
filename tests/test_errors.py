"""Tests nuevos de la etapa 3: el formato estándar de errores (RFC 7807)."""
API = "/api/v1/products"


def test_not_found_uses_problem_details(client):
    r = client.get(f"{API}/42")
    assert r.status_code == 404
    assert r.headers["content-type"] == "application/problem+json"
    body = r.json()
    assert body["type"].endswith("/not-found")
    assert body["detail"] == "Producto 42 no existe"
    assert body["instance"] == f"{API}/42"


def test_validation_errors_list_each_field(client):
    r = client.post(API, json={"sku": "mal sku", "name": "X", "price": "-1"})
    assert r.status_code == 400
    fields = {e["field"] for e in r.json()["errors"]}
    assert {"sku", "price"} <= fields


def test_unknown_route_also_uses_problem_details(client):
    r = client.get("/api/v1/no-existe")
    assert r.status_code == 404
    assert r.headers["content-type"] == "application/problem+json"
