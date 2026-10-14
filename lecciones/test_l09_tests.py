"""
LECCIÓN 9: Probar tu API automáticamente (pytest + TestClient)
==============================================================

Probar a mano en /docs no escala: con 30 endpoints, cada cambio te obligaría a
revisar todo de nuevo. Los tests automáticos lo hacen en segundos.

Conceptos:
- TestClient simula peticiones HTTP sin levantar un servidor.
- Cada test: PREPARAR datos -> ACTUAR (hacer la petición) -> VERIFICAR (assert).
- Los tests deben ser independientes: cada uno empieza con datos limpios (fixture).
- Prueba también los casos de error: 404, 409, 422. Ahí viven los bugs.

Ejecutar (desde la carpeta lecciones/):
    pytest -v test_l09_tests.py

Este archivo prueba la API de la lección 6 (l06_crud.py).
"""
import pytest
from fastapi.testclient import TestClient

import l06_crud
from l06_crud import app

client = TestClient(app)

POLO = {"sku": "POLO-001", "nombre": "Polo básico", "precio": "39.90", "stock": 10}


# Una "fixture" con autouse=True se ejecuta antes de CADA test:
# vacía la base de datos en memoria para que ningún test dependa de otro.
@pytest.fixture(autouse=True)
def base_de_datos_limpia():
    l06_crud.DB.clear()
    l06_crud.contador = 0


def test_crear_devuelve_201_y_location():
    r = client.post("/products", json=POLO)              # ACTUAR

    assert r.status_code == 201                           # VERIFICAR
    assert r.json()["id"] == 1
    assert r.headers["location"] == "/products/1"


def test_sku_duplicado_devuelve_409():
    client.post("/products", json=POLO)                   # PREPARAR
    r = client.post("/products", json=POLO)               # ACTUAR
    assert r.status_code == 409                           # VERIFICAR


def test_precio_invalido_devuelve_422():
    r = client.post("/products", json={**POLO, "precio": "0"})
    assert r.status_code == 422


def test_leer_inexistente_devuelve_404():
    assert client.get("/products/999").status_code == 404


def test_patch_solo_cambia_lo_enviado():
    client.post("/products", json=POLO)

    r = client.patch("/products/1", json={"precio": "35.00"})

    assert r.json()["precio"] == "35.00"
    assert r.json()["stock"] == 10        # no se perdió


def test_borrar_y_ya_no_existe():
    client.post("/products", json=POLO)
    assert client.delete("/products/1").status_code == 204
    assert client.get("/products/1").status_code == 404


# RETO 1: escribe un test que compruebe que GET /products?con_stock=true filtra bien
#         (crea un producto con stock 0 y otro con stock 5).
# RETO 2: escribe un test que compruebe que PUT sin "stock" lo deja en 0.
# RETO 3: rompe a propósito l06_crud.py (por ejemplo, quita exclude_unset=True)
#         y comprueba que algún test falla. Así sabes que tus tests sirven.
