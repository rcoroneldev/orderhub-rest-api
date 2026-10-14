"""
LECCIÓN 6: CRUD completo y manejo de errores
============================================

CRUD = Create, Read, Update, Delete. Es el núcleo de casi cualquier API REST.

    Acción                 Método   URL                 Respuesta OK
    ---------------------  -------  ------------------  ------------
    Crear                  POST     /products           201 + el recurso creado
    Listar                 GET      /products           200 + lista
    Leer uno               GET      /products/{id}      200 + recurso
    Reemplazar completo    PUT      /products/{id}      200 + recurso
    Modificar una parte    PATCH    /products/{id}      200 + recurso
    Borrar                 DELETE   /products/{id}      204 sin cuerpo

Conceptos nuevos:
- HTTPException: corta la ejecución y responde un error con el código que elijas.
- PUT vs PATCH: PUT reemplaza TODO el recurso; PATCH cambia solo los campos enviados.
- model_dump(exclude_unset=True): la pieza que hace funcionar un PATCH correctamente.
- Cabecera Location: en un 201 indica la URL del recurso nuevo.

Ejecutar:
    uvicorn l06_crud:app --reload

Prueba este recorrido en /docs, en orden:
    1. POST   /products   {"sku": "POLO-001", "nombre": "Polo", "precio": "39.90", "stock": 10}
                                       -> 201 (repite el mismo SKU: 409)
    2. GET    /products                -> lo ves en la lista
    3. PATCH  /products/1  {"precio": "35.00"}      -> solo cambia el precio
    4. PUT    /products/1  sin "stock"              -> ¡el stock vuelve a 0! (PUT reemplaza todo)
    5. DELETE /products/1              -> 204
    6. GET    /products/1              -> 404
"""
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="OrderHub - Lección 6: CRUD")

SKU_VALIDO = r"^[A-Z0-9-]{3,30}$"


# ---------- Modelos ----------
class ProductoCrear(BaseModel):
    sku: str = Field(pattern=SKU_VALIDO, examples=["POLO-001"])
    nombre: str = Field(min_length=2)
    precio: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)


class ProductoActualizar(BaseModel):
    """Para PATCH: TODOS los campos son opcionales. El SKU no se puede cambiar."""
    nombre: str | None = Field(default=None, min_length=2)
    precio: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)


class Producto(ProductoCrear):
    """Salida: todo lo de ProductoCrear + el id (herencia de clases)."""
    id: int


# ---------- "Base de datos" en memoria ----------
DB: dict[int, Producto] = {}
contador = 0


# ---------- Función auxiliar: buscar o lanzar 404 ----------
def buscar_o_404(product_id: int) -> Producto:
    producto = DB.get(product_id)
    if producto is None:
        # raise detiene la función; FastAPI responde con este código y mensaje
        raise HTTPException(status_code=404, detail=f"Producto {product_id} no existe")
    return producto


# ---------- Endpoints ----------
@app.post("/products", response_model=Producto, status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoCrear, response: Response):
    global contador
    if any(p.sku == datos.sku for p in DB.values()):
        raise HTTPException(status_code=409, detail=f"Ya existe un producto con SKU '{datos.sku}'")

    contador += 1
    nuevo = Producto(id=contador, **datos.model_dump())
    DB[nuevo.id] = nuevo
    response.headers["Location"] = f"/products/{nuevo.id}"
    return nuevo


@app.get("/products", response_model=list[Producto])
def listar(con_stock: bool | None = None):
    productos = list(DB.values())
    if con_stock is not None:
        productos = [p for p in productos if (p.stock > 0) == con_stock]
    return productos


@app.get("/products/{product_id}", response_model=Producto)
def leer(product_id: int):
    return buscar_o_404(product_id)


@app.put("/products/{product_id}", response_model=Producto)
def reemplazar(product_id: int, datos: ProductoCrear):
    buscar_o_404(product_id)
    actualizado = Producto(id=product_id, **datos.model_dump())  # se reemplaza todo
    DB[product_id] = actualizado
    return actualizado


@app.patch("/products/{product_id}", response_model=Producto)
def modificar(product_id: int, cambios: ProductoActualizar):
    actual = buscar_o_404(product_id)
    # exclude_unset=True -> SOLO los campos que el cliente envió de verdad.
    # Sin esto, los campos no enviados (None) borrarían los valores actuales.
    solo_enviados = cambios.model_dump(exclude_unset=True)
    actualizado = actual.model_copy(update=solo_enviados)
    DB[product_id] = actualizado
    return actualizado


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(product_id: int):
    buscar_o_404(product_id)
    del DB[product_id]
    # 204: no se devuelve nada


# RETO 1: cambia exclude_unset=True por False. ¿Qué pasa al hacer PATCH solo con el precio?
#         Este bug es muy común en APIs reales.
# RETO 2: añade POST /products/{id}/descontinuar que marque "activo": false.
#         Si ya estaba descontinuado, responde 409.
