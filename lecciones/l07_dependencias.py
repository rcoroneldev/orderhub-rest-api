"""
LECCIÓN 7: Dependencias (Depends)
=================================

Problema: varias rutas necesitan lo mismo (paginación, comprobar quién llama,
una conexión a la base de datos...). No queremos copiar ese código en cada una.

Solución: una DEPENDENCIA es una función que FastAPI ejecuta ANTES de tu endpoint.
Su resultado se pasa como argumento. Si lanza un error, el endpoint ni se ejecuta.

    def mi_endpoint(valor = Depends(mi_dependencia)): ...

Es la base de la autenticación, del acceso a la base de datos (lección 8)
y de los tests (lección 9: las dependencias se pueden reemplazar).

Ejecutar:
    uvicorn l07_dependencias:app --reload

Probar:
    /products?pagina=2&tamano=2                     -> público y paginado
    /orders                                         -> 401: falta la API key
    En /docs pulsa "Authorize" o envía la cabecera:
      curl localhost:8000/orders -H "X-API-Key: clave-cliente"                      -> solo sus pedidos
      curl localhost:8000/orders -H "X-API-Key: clave-admin"                        -> todos
      curl -X DELETE localhost:8000/products/1 -H "X-API-Key: clave-cliente"        -> 403
      curl -X DELETE localhost:8000/products/1 -H "X-API-Key: clave-admin"          -> 204
"""
from dataclasses import dataclass

from fastapi import Depends, FastAPI, HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader

app = FastAPI(title="OrderHub - Lección 7: dependencias")

PRODUCTS = [{"id": i, "nombre": f"Producto {i}"} for i in range(1, 8)]
ORDERS = [
    {"id": 1, "cliente": "luis", "total": "79.80"},
    {"id": 2, "cliente": "maria", "total": "129.00"},
    {"id": 3, "cliente": "luis", "total": "25.50"},
]


# ---------- Dependencia 1: parámetros de paginación reutilizables ----------
@dataclass
class Paginacion:
    pagina: int
    tamano: int

    @property
    def inicio(self) -> int:
        return (self.pagina - 1) * self.tamano


def paginacion(pagina: int = Query(1, ge=1), tamano: int = Query(3, ge=1, le=50)) -> Paginacion:
    return Paginacion(pagina, tamano)


# ---------- Dependencia 2: identificar a quien llama (API key) ----------
# Simulamos usuarios. En la etapa 5 del proyecto esto se reemplaza por login con JWT.
CLAVES = {
    "clave-cliente": {"usuario": "luis", "rol": "customer"},
    "clave-admin": {"usuario": "ana", "rol": "admin"},
}
cabecera_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)  # botón "Authorize" en /docs


def usuario_actual(api_key: str | None = Security(cabecera_api_key)) -> dict:
    if api_key is None or api_key not in CLAVES:
        # 401 = "no sé quién eres"
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="API key ausente o inválida")
    return CLAVES[api_key]


# ---------- Dependencia 3: una dependencia que USA otra dependencia ----------
def solo_admin(usuario: dict = Depends(usuario_actual)) -> dict:
    if usuario["rol"] != "admin":
        # 403 = "sé quién eres, pero no tienes permiso"
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin")
    return usuario


# ---------- Endpoints ----------
@app.get("/products")
def listar_productos(p: Paginacion = Depends(paginacion)):
    return {"pagina": p.pagina, "items": PRODUCTS[p.inicio: p.inicio + p.tamano]}


@app.get("/orders")
def mis_pedidos(usuario: dict = Depends(usuario_actual)):
    # Un cliente solo ve sus pedidos; un admin ve todos.
    if usuario["rol"] == "admin":
        return ORDERS
    return [o for o in ORDERS if o["cliente"] == usuario["usuario"]]


@app.delete("/products/{product_id}", status_code=204)
def borrar_producto(product_id: int, admin: dict = Depends(solo_admin)):
    print(f"{admin['usuario']} borró el producto {product_id}")


# RETO: crea una dependencia "registrar_peticion" que imprima la hora de cada petición
# y aplícala a TODAS las rutas a la vez con: app = FastAPI(dependencies=[Depends(...)])
