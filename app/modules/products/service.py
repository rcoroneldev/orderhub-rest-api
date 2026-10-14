"""SERVICE: las reglas de negocio de productos.

- No sabe nada de HTTP: no usa Request, Response ni HTTPException.
- Lanza errores de dominio (NotFound, Conflict); core/errors.py los traduce a HTTP.
- Usa el repository para leer y guardar; nunca escribe SQL directamente.

Ventaja: en la etapa 4, el service de pedidos podrá llamar a ProductService
(por ejemplo, para comprobar stock) sin pasar por HTTP.
"""
from sqlalchemy.orm import Session

from app.common.pagination import PageParams, apply_sort, paginate
from app.core.errors import Conflict, NotFound

from .models import Product
from .repository import ProductRepository
from .schemas import ProductCreate, ProductFilters, ProductUpdate

SORTABLE = {"name": Product.name, "price": Product.price, "created_at": Product.created_at}


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def create(self, data: ProductCreate) -> Product:
        if self.repo.get_by_sku(data.sku):
            raise Conflict(f"Ya existe el SKU '{data.sku}'")
        return self.repo.add(Product(**data.model_dump()))

    def get(self, product_id: int) -> Product:
        product = self.repo.get(product_id)
        if product is None:
            raise NotFound(f"Producto {product_id} no existe")
        return product

    def search(self, filters: ProductFilters, sort: str, params: PageParams) -> dict:
        stmt = self.repo.search_query(filters)
        stmt = apply_sort(stmt, sort, SORTABLE).order_by(Product.id)  # id: desempate estable
        return paginate(self.db, stmt, params)

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self.get(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        return self.repo.save(product)

    def delete(self, product_id: int) -> None:
        # Etapa 4: aquí se añadirá la regla "no borrar productos con pedidos";
        # se desactivarán (is_active = False) en lugar de borrarlos.
        self.repo.delete(self.get(product_id))
