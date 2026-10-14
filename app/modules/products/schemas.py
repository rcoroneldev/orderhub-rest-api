"""Contrato de la API de productos (Pydantic). Igual que en las etapas 1 y 2."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(pattern=r"^[A-Z0-9-]{3,30}$", examples=["POLO-001"])
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2, examples=["39.90"])
    stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    """PATCH: todo opcional. El SKU es el identificador de negocio y no se modifica."""
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductFilters(BaseModel):
    """Agrupa los filtros de búsqueda para pasarlos limpios del router al service."""
    search: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    in_stock: bool | None = None
