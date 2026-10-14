"""
LECCIÓN 5: Controlar la respuesta (response_model y códigos de estado)
======================================================================

Conceptos:
- Los CÓDIGOS DE ESTADO HTTP le dicen al cliente qué pasó, sin leer el cuerpo:
    200 OK            -> todo bien (por defecto)
    201 Created       -> se creó algo nuevo (en POST)
    204 No Content    -> todo bien, sin nada que devolver (típico en DELETE)
    400/422           -> el cliente envió algo mal
    404 Not Found     -> el recurso no existe
    409 Conflict      -> choca con el estado actual (un duplicado, sin stock...)
    500               -> error del servidor: un bug tuyo
- response_model define la forma EXACTA de la salida:
    * filtra campos que no deben salir (costos internos, secretos)
    * documenta la respuesta en /docs
- Patrón clave: un modelo para lo que ENTRA y otro para lo que SALE.

Ejecutar:
    uvicorn l05_respuestas:app --reload

Probar:
    POST /products con {"sku": "POLO-001", "nombre": "Polo", "precio": "39.90", "costo": "18.00"}
    -> responde 201 y el "costo" NO aparece (el cliente no debe ver tu margen).
    GET /products/1 -> tampoco aparece, aunque está guardado.
"""
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(title="OrderHub - Lección 5: respuestas")


class ProductoEntrada(BaseModel):
    """Lo que el cliente ENVÍA."""
    sku: str
    nombre: str
    precio: Decimal = Field(gt=0)
    costo: Decimal | None = None   # dato interno: se guarda, pero NUNCA se devuelve


class ProductoSalida(BaseModel):
    """Lo que la API DEVUELVE. No tiene 'costo', pero sí id y fecha de creación."""
    id: int
    sku: str
    nombre: str
    precio: Decimal
    creado_en: datetime


DB: dict[int, dict] = {}
siguiente_id = 1


@app.post("/products", response_model=ProductoSalida, status_code=status.HTTP_201_CREATED)
def crear(producto: ProductoEntrada):
    global siguiente_id
    registro = {**producto.model_dump(), "id": siguiente_id, "creado_en": datetime.now(timezone.utc)}
    DB[siguiente_id] = registro
    siguiente_id += 1
    # Devolvemos el registro COMPLETO (con costo), pero response_model lo filtra.
    return registro


@app.get("/products/{product_id}", response_model=ProductoSalida)
def obtener(product_id: int):
    return DB[product_id]  # si no existe falla con 500: lo arreglamos en la lección 6


@app.get("/products", response_model=list[ProductoSalida])  # una lista de salidas
def listar():
    return list(DB.values())


# RETO 1: pide GET /products/999. ¿Qué código recibes? ¿Por qué es incorrecto?
# RETO 2: crea GET /admin/products/{id} con otro modelo de salida que SÍ incluya
#         "costo" y "margen" (precio - costo).
