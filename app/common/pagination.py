"""Paginación y ordenamiento reutilizables por cualquier módulo (productos, pedidos...)."""
import math
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.errors import BusinessRuleViolation

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Respuesta paginada genérica: Page[ProductOut], Page[OrderOut]..."""
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


class PageParams:
    """Se usa como dependencia: `params: PageParams = Depends()` (lección 7)."""

    def __init__(self, page: int = Query(1, ge=1, description="Número de página, desde 1"),
                 size: int = Query(20, ge=1, le=100, description="Elementos por página, máx. 100")):
        self.page = page
        self.size = size


def apply_sort(stmt: Select, sort: str, allowed: dict) -> Select:
    """`sort=-price` -> ORDER BY price DESC. Solo campos de la lista blanca `allowed`."""
    field = sort.lstrip("-")
    if field not in allowed:
        raise BusinessRuleViolation(f"No se puede ordenar por '{field}'. Opciones: {sorted(allowed)}")
    column = allowed[field]
    return stmt.order_by(column.desc() if sort.startswith("-") else column.asc())


def paginate(db: Session, stmt: Select, params: PageParams) -> dict:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery()))
    items = db.scalars(stmt.offset((params.page - 1) * params.size).limit(params.size)).all()
    return {"items": items, "total": total, "page": params.page, "size": params.size,
            "pages": math.ceil(total / params.size) if total else 0}
