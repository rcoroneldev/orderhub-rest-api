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
    1: {"id": 1, "Name": "Polo básico", "categoria": "ropa", "precio": 39.90},
    2: {"id": 2, "Name": "Headphones", "categoria": "electronica", "precio": 129.00},
    3: {"id": 3, "Name": "Taza térmica", "categoria": "hogar", "precio": 25.50},
    4: {"id": 4, "Name": "Cellphone", "categoria": "electronica", "precio": 145.00},
    5: {"id": 5, "Name": "Laptop", "categoria": "electronica", "precio": 999.00},
    6: {"id": 6, "Name": "Tablet", "categoria": "electronica", "precio": 399.00},
    7: {"id": 7, "Name": "Balón de fútbol", "categoria": "sports", "precio": 29.90},
    8: {"id": 8, "Name": "Camiseta deportiva", "categoria": "ropa", "precio": 25.00},
    9: {"id": 9, "Name": "Zapatillas", "categoria": "sports", "precio": 89.90},
    10: {"id": 10, "Name": "Gorra", "categoria": "ropa", "precio": 15.00}
}


# Ruta FIJA: debe ir antes que /products/{product_id}.
# Si estuviera después, FastAPI intentaría convertir "destacado" a int y respondería 422.
@app.get("/products/destacado")
def producto_destacado():
    return PRODUCTS[5]


# Ejercicio 3: también es ruta FIJA, así que va antes que /products/{product_id}.
@app.get("/products/mas_caro")
def obtener_producto_mas_caro():
    producto = max(PRODUCTS.values(), key=lambda p: p["precio"])
    return {"producto": producto}


@app.get("/products/{product_id}")
def obtener_producto(product_id: int):  # <- int vali da y convierte"1" -> 1
    producto = PRODUCTS.get(product_id)
    print(f"obtener_producto({product_id}) -> {producto}")
    if producto is None:
        return {"error": f"No existe el producto {product_id}"}
    return producto

# Enum: restringe los valores posibles. Además aparecen como desplegable en /docs.
class Categoria(str, Enum):
    ropa = "ropa"
    electronica = "electronica"
    hogar = "hogar"
    sports = "sports"


@app.get("/categorias/{categoria}")
def productos_por_categoria(categoria: Categoria):
    resultado = [p for p in PRODUCTS.values() if p["categoria"] == categoria.value]
    return {"categoria": categoria, "productos": resultado}


# RETO: crea GET /products/{product_id}/precio que devuelva solo el precio del producto.
@app.get("/products/{product_id}/precio")
def obtener_precio(product_id: int):
    producto = PRODUCTS.get(product_id)
    if producto is None:
        return {"error": f"No existe el producto {product_id}"}
    return {"precio": producto["precio"]}

#  Ejercicio 1: nombre de un producto (calentamiento)
@app.get("/products/{product_id}/nombre")
def obtener_nombre_producto(product_id: int):
    producto = PRODUCTS.get(product_id)
    if producto is None:
        return {"Error Message": f"No existe el producto {product_id}"}
    return {"nombre": producto["Name"]}
# Ejercicio 2: cantidad por categoría
@app.get("/categorias/{categoria}/total")
def cantidad_por_categoria(categoria: Categoria):
    resultado = [p for p in PRODUCTS.values() if p["categoria"] == categoria.value]
    print(f"cantidad_por_categoria({categoria}) -> {len(resultado)}")
    return {"categoria": categoria, "total": len(resultado)}

# Ejercicio 4: dos parámetros en la misma ruta
@app.get("/products/{product_id}/categorias/{categoria}")
def obtener_producto_por_categoria(product_id: int, categoria: Categoria):
    producto = PRODUCTS.get(product_id)
    if producto is None:
        return {"error": f"No existe el producto {product_id}"}
    if producto["categoria"] != categoria.value:
        return {"error": f"El producto {product_id} no pertenece a la categoría {categoria}"}
    return {"producto": producto, "categoria": categoria}

#Ejercicio 5: descuento con validación (concepto nuevo)
@app.get("/products/{product_id}/descuento/{porcentaje}")
def obtener_descuento(product_id: int, porcentaje: int):
    producto = PRODUCTS.get(product_id)
    if producto is None:
        return {"error": f"No existe el producto {product_id}"}
    precio_original = producto["precio"]
    precio_final = precio_original - (precio_original * porcentaje / 100)
    return {"precio_original": precio_original, "porcentaje": porcentaje, "precio_final": precio_final}

