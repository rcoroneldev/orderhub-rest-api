"""
LECCIÓN 3: Parámetros de consulta (query parameters)
====================================================

Conceptos:
- Van después del "?" en la URL:  /products?categoria=ropa&limite=2
- Examples
- /products?categoria=sports&con_stock=true&precio_max=50&limite=4
- /products?categoria=electronica&precio=150&limite=5
- Sirven para FILTRAR, BUSCAR, ORDENAR y PAGINAR, no para identificar un recurso.
  (Para identificar uno: ruta, /products/1. Para filtrar varios: query.)
- Cualquier argumento de la función que NO esté en la ruta es un query parameter.
- Con valor por defecto es opcional; sin valor por defecto es obligatorio.
- Query(...) añade validaciones: mínimo, máximo, descripción.

Ejecutar:
    uvicorn l03_parametros_query:app --reload

Probar:
    /products                               -> todos
    /products?categoria=ropa                -> filtrado
    /products?con_stock=true                -> FastAPI convierte "true" a bool
    /products?precio_max=50                 -> rango de precio
    /products?limite=2&saltar=2             -> paginación simple
    /products?limite=500                    -> 422: supera el máximo de 100
    /buscar                                 -> 422: 'texto' es obligatorio
    /buscar?texto=polo
"""
from typing import Optional

from fastapi import FastAPI, Query

app = FastAPI(title="OrderHub - Lección 3: parámetros de consulta")

PRODUCTS = [
    {"id": 1, "nombre": "Polo básico", "categoria": "ropa", "precio": 39.90, "stock": 50},
    {"id": 2, "nombre": "Polo deportivo", "categoria": "ropa", "precio": 59.90, "stock": 0},
    {"id": 3, "nombre": "Audífonos", "categoria": "electronica", "precio": 129.00, "stock": 12},
    {"id": 4, "nombre": "Cargador USB-C", "categoria": "electronica", "precio": 45.00, "stock": 30},
    {"id": 5, "nombre": "Taza térmica", "categoria": "hogar", "precio": 25.50, "stock": 0},
]


@app.get("/products")
def listar_productos(
    categoria: Optional[str] = None,        # opcional: None significa "no filtrar"
    con_stock: Optional[bool] = None,       # opcional, se convierte de texto a bool
    precio_max: Optional[float] = Query(None, gt=0),
    saltar: int = Query(0, ge=0),           # ge = "mayor o igual que"
    limite: int = Query(10, ge=1, le=100, description="Máximo de resultados"),
):
    resultado = PRODUCTS
    if categoria is not None:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    if con_stock is not None:
        resultado = [p for p in resultado if (p["stock"] > 0) == con_stock]
    if precio_max is not None:
        resultado = [p for p in resultado if p["precio"] <= precio_max]

    total = len(resultado)
    pagina = resultado[saltar: saltar + limite]
    return {"total": total, "saltar": saltar, "limite": limite, "items": pagina}


@app.get("/buscar")
def buscar(NombreProducto: str = Query(min_length=2)):  # sin valor por defecto = OBLIGATORIO
    return [p for p in PRODUCTS if NombreProducto.lower() in p["nombre"].lower()]


# RETO: añade a /products un parámetro "orden" que acepte "precio" o "-precio"
# (descendente) y ordene el resultado. Pista: sorted(..., key=..., reverse=...)
