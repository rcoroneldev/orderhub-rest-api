"""
LECCIÓN 2: Parámetros de ruta (path parameters)
===============================================

Conceptos:
- Una parte de la URL puede ser variable: /products/{product_id}
- El "type hint" de Python (product_id: int) hace que FastAPI CONVIERTA y VALIDE el valor.
- Si el valor no es válido, FastAPI responde 422 solo, sin que escribas código.
- El orden de las rutas importa: las fijas van ANTES que las variables.

Ejecutar:
    uvicorn l02_parametros_ruta:app --reload

Probar:
    /products/1             -> encuentra el producto
    /products/99            -> no existe (por ahora un mensaje; en la lección 6 aprenderás el 404)
    /products/abc           -> 422: "abc" no es un entero. ¡Lee el detalle del error!
    /products/destacado     -> ruta fija
    /categorias/ropa        -> parámetro con valores permitidos (Enum)
    /categorias/juguetes    -> 422: no está en la lista
"""
from enum import Enum

from fastapi import FastAPI

app = FastAPI(title="OrderHub - Lección 2: parámetros de ruta")

# Datos de ejemplo en memoria (en la lección 8 vendrán de una base de datos)
PRODUCTS = {
    1: {"id": 1, "nombre": "Polo básico", "categoria": "ropa", "precio": 39.90},
    2: {"id": 2, "nombre": "Audífonos", "categoria": "electronica", "precio": 129.00},
    3: {"id": 3, "nombre": "Taza térmica", "categoria": "hogar", "precio": 25.50},
}


# Ruta FIJA: debe ir antes que /products/{product_id}.
# Si estuviera después, FastAPI intentaría convertir "destacado" a int y respondería 422.
@app.get("/products/destacado")
def producto_destacado():
    return PRODUCTS[2]


@app.get("/products/{product_id}")
def obtener_producto(product_id: int):  # <- int valida y convierte "1" -> 1
    producto = PRODUCTS.get(product_id)
    if producto is None:
        return {"error": f"No existe el producto {product_id}"}
    return producto


# Enum: restringe los valores posibles. Además aparecen como desplegable en /docs.
class Categoria(str, Enum):
    ropa = "ropa"
    electronica = "electronica"
    hogar = "hogar"


@app.get("/categorias/{categoria}")
def productos_por_categoria(categoria: Categoria):
    resultado = [p for p in PRODUCTS.values() if p["categoria"] == categoria.value]
    return {"categoria": categoria, "productos": resultado}


# RETO: crea GET /products/{product_id}/precio que devuelva solo el precio del producto.
