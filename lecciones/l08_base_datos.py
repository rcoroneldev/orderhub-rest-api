"""
LECCIÓN 8: Guardar datos en una base de datos (SQLite + SQLAlchemy)
===================================================================

Hasta ahora los datos se perdían al reiniciar el servidor. Ahora se guardan en
un archivo SQLite (curso.db) usando SQLAlchemy, el ORM más usado en Python.

Conceptos:
- ORM: escribes clases de Python y SQLAlchemy genera el SQL (CREATE, INSERT, SELECT...).
- Hay DOS tipos de modelos, con trabajos distintos:
    * Modelo SQLAlchemy (ProductoDB)    -> cómo se GUARDA en la tabla
    * Modelo Pydantic (ProductoSalida)  -> cómo se ENVÍA por la API
- Sesión: una "conversación" con la base de datos. Una por petición, siempre cerrada.
- get_db es una dependencia con "yield": lo que va después del yield se ejecuta
  al terminar la petición, ideal para cerrar la sesión.
- from_attributes=True permite a Pydantic leer un objeto SQLAlchemy directamente.

Ejecutar:
    uvicorn l08_base_datos:app --reload

Probar:
    1. Crea 2 o 3 productos con POST /products.
    2. Detén el servidor (Ctrl+C) y arráncalo de nuevo.
    3. GET /products -> ¡siguen ahí! Se ha creado el archivo curso.db.
    (Para ver la tabla por dentro, usa la extensión "SQLite Viewer" de VS Code.)
"""
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, Integer, Numeric, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# ---------- 1. Configurar la conexión ----------
engine = create_engine("sqlite:///./curso.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


# ---------- 2. Modelo de la TABLA (SQLAlchemy) ----------
class ProductoDB(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)           # autoincremental
    sku: Mapped[str] = mapped_column(String(30), unique=True)
    nombre: Mapped[str] = mapped_column(String(120))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))     # dinero: Numeric, no Float
    stock: Mapped[int] = mapped_column(Integer, default=0)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)  # crea la tabla si no existe


# ---------- 3. Modelos de la API (Pydantic) ----------
class ProductoCrear(BaseModel):
    sku: str = Field(pattern=r"^[A-Z0-9-]{3,30}$")
    nombre: str = Field(min_length=2)
    precio: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)


class ProductoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # leer desde objetos SQLAlchemy

    id: int
    sku: str
    nombre: str
    precio: Decimal
    stock: int
    creado_en: datetime


# ---------- 4. Dependencia: una sesión por petición ----------
def get_db():
    db = SessionLocal()
    try:
        yield db          # aquí se ejecuta tu endpoint
    finally:
        db.close()        # se ejecuta SIEMPRE al terminar, incluso si hubo un error


app = FastAPI(title="OrderHub - Lección 8: base de datos")


# ---------- 5. Endpoints ----------
@app.post("/products", response_model=ProductoSalida, status_code=status.HTTP_201_CREATED)
def crear(datos: ProductoCrear, db: Session = Depends(get_db)):
    existe = db.scalar(select(ProductoDB).where(ProductoDB.sku == datos.sku))
    if existe:
        raise HTTPException(409, detail=f"Ya existe un producto con SKU '{datos.sku}'")

    nuevo = ProductoDB(**datos.model_dump())
    db.add(nuevo)        # prepara el INSERT
    db.commit()          # lo ejecuta y confirma
    db.refresh(nuevo)    # recarga el objeto para obtener el id generado
    return nuevo         # Pydantic lo convierte gracias a from_attributes


@app.get("/products", response_model=list[ProductoSalida])
def listar(con_stock: bool | None = None, db: Session = Depends(get_db)):
    consulta = select(ProductoDB).order_by(ProductoDB.id)
    if con_stock is True:
        consulta = consulta.where(ProductoDB.stock > 0)     # se va armando el SELECT
    elif con_stock is False:
        consulta = consulta.where(ProductoDB.stock == 0)
    return db.scalars(consulta).all()


@app.get("/products/{product_id}", response_model=ProductoSalida)
def leer(product_id: int, db: Session = Depends(get_db)):
    producto = db.get(ProductoDB, product_id)   # búsqueda por clave primaria
    if producto is None:
        raise HTTPException(404, detail=f"Producto {product_id} no existe")
    return producto


@app.delete("/products/{product_id}", status_code=204)
def borrar(product_id: int, db: Session = Depends(get_db)):
    producto = db.get(ProductoDB, product_id)
    if producto is None:
        raise HTTPException(404, detail=f"Producto {product_id} no existe")
    db.delete(producto)
    db.commit()


# RETO 1: añade PATCH /products/{id} con lo aprendido en la lección 6
#         (pista: setattr(producto, campo, valor) por cada campo enviado, y luego commit).
# RETO 2: añade una columna "descripcion". Ojo: create_all NO modifica tablas existentes.
#         Borra curso.db para que se cree de nuevo. Las migraciones con Alembic resuelven
#         esto en proyectos reales; las verás en la etapa 6.
