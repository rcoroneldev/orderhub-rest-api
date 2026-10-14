"""
LECCIÓN 4: Recibir datos en el cuerpo (body) con Pydantic
=========================================================

Conceptos:
- Para CREAR algo usamos POST y enviamos los datos en el cuerpo, en formato JSON.
- Pydantic define la "forma" que deben tener esos datos mediante una clase.
- FastAPI lee el JSON, lo valida contra la clase y te entrega un objeto de Python.
- Si algo no cumple las reglas, responde 422 explicando QUÉ campo falló y POR QUÉ.
  No escribes ni un if para validar.
- El dinero se representa con Decimal, nunca con float (0.1 + 0.2 != 0.3 en float).

Ejecutar:
    uvicorn l04_body_pydantic:app --reload

Probar (más fácil desde /docs con "Try it out"):

    curl -X POST localhost:8000/products -H "Content-Type: application/json" \
      -d '{"sku": "POLO-001", "nombre": "Polo básico", "precio": "39.90", "stock": 50}'

    Ahora rómpelo a propósito y lee el error:
      - quita "nombre"             -> campo obligatorio
      - "sku": "polo 1"            -> no cumple el patrón (MAYÚSCULAS, números y guiones)
      - "precio": "0"              -> debe ser mayor que 0
      - "precio": "39.999"         -> máximo 2 decimales
      - "stock": -5                -> debe ser >= 0
"""
from decimal import Decimal

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="OrderHub - Lección 4: body con Pydantic")


class ProductoNuevo(BaseModel):
    # Obligatorio y con regla: mayúsculas, números y guiones, de 3 a 30 caracteres
    sku: str = Field(pattern=r"^[A-Z0-9-]{3,30}$", examples=["POLO-001"])
    nombre: str = Field(min_length=2, max_length=120)
    # Decimal con como máximo 2 decimales y estrictamente mayor que 0
    precio: Decimal = Field(gt=0, decimal_places=2, examples=["39.90"])
    # Campos opcionales: tienen valor por defecto
    stock: int = Field(default=0, ge=0)
    descripcion: str = ""
    etiquetas: list[str] = []


@app.post("/products")
def crear_producto(producto: ProductoNuevo):  # <- es un BaseModel, así que viene del BODY
    # 'producto' ya es un objeto validado: se usa con punto, con autocompletado en el editor
    print("Recibido:", producto.sku, producto.precio)

    valor_inventario = producto.precio * producto.stock   # Decimal * int = Decimal exacto
    return {
        "mensaje": "Producto recibido",
        # str(): en un diccionario libre, FastAPI convertiría el Decimal a float y perdería
        # exactitud. (Con response_model, lección 5, Pydantic lo serializa bien por ti.)
        "valor_inventario": str(valor_inventario),
        "datos": producto.model_dump(),   # model_dump() lo convierte de vuelta a diccionario
    }


# Se pueden combinar los tres tipos de parámetros en una misma ruta:
#   ruta (product_id), query (notificar) y body (producto)
@app.put("/products/{product_id}")
def reemplazar_producto(product_id: int, producto: ProductoNuevo, notificar: bool = False):
    return {"id": product_id, "notificar": notificar, "datos": producto.model_dump()}


# RETO: añade un campo "categoria" que solo acepte ropa, electronica u hogar,
# con "hogar" por defecto. Pista: un Enum, como en la lección 2.
