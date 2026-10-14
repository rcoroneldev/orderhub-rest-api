"""REPOSITORY: la única capa que habla con la base de datos para productos.

Aquí solo hay SQL (vía SQLAlchemy): ni reglas de negocio ni HTTP.
Si mañana cambias de base de datos u ORM, solo cambia este archivo.
"""
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from .models import Product
from .schemas import ProductFilters


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.sku == sku))

    def search_query(self, f: ProductFilters) -> Select:
        stmt = select(Product)
        if f.search:
            stmt = stmt.where(Product.name.ilike(f"%{f.search}%"))
        if f.min_price is not None:
            stmt = stmt.where(Product.price >= f.min_price)
        if f.max_price is not None:
            stmt = stmt.where(Product.price <= f.max_price)
        if f.in_stock is True:
            stmt = stmt.where(Product.stock > 0)
        elif f.in_stock is False:
            stmt = stmt.where(Product.stock == 0)
        return stmt

    def add(self, product: Product) -> Product:
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def save(self, product: Product) -> Product:
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()
