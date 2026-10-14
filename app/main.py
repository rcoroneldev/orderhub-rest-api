"""
OrderHub API - ETAPA 3: arquitectura en capas
=============================================

Qué cambió respecto a la etapa 2:
- Cada módulo de negocio (products; luego customers y orders) tiene su carpeta con:
      router.py      -> HTTP: rutas, validación de entrada, códigos de estado
      service.py     -> reglas de negocio (no sabe nada de HTTP)
      repository.py  -> acceso a datos (lo único que escribe SQL)
      schemas.py     -> contrato de la API (Pydantic)
      models.py      -> tablas (SQLAlchemy)
- Piezas compartidas: core/ (configuración, errores), db/ (sesión), common/ (paginación).
- Todos los errores siguen el formato RFC 7807.

Qué NO cambió: el contrato. Los tests de tests/test_products.py siguen idénticos.

Ejecutar:   uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.errors import register_error_handlers
from app.db.session import Base, engine
from app.modules.products.router import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Etapa 6: se reemplaza por migraciones con Alembic
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan,
                  description="Gestión de productos, clientes y pedidos. Etapa 3.")
    register_error_handlers(app)
    app.include_router(products_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["Ops"], summary="El servicio está vivo")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
