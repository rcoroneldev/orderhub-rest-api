"""ROUTER: traduce HTTP <-> service. Compáralo con app/main.py de la etapa 2:
cada función ahora tiene 1 o 2 líneas, porque ya no decide nada ni escribe SQL.
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.common.pagination import Page, PageParams
from app.db.session import get_db

from .schemas import ProductCreate, ProductFilters, ProductOut, ProductUpdate
from .service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


def get_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)


def get_filters(
    search: str | None = Query(None, description="Texto en el nombre"),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    in_stock: bool | None = None,
) -> ProductFilters:
    return ProductFilters(search=search, min_price=min_price, max_price=max_price, in_stock=in_stock)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED,
             summary="Crear un producto")
def create_product(data: ProductCreate, request: Request, response: Response,
                   service: ProductService = Depends(get_service)):
    product = service.create(data)
    response.headers["Location"] = f"{request.url.path}/{product.id}"
    return product


@router.get("", response_model=Page[ProductOut], summary="Buscar productos")
def list_products(
    filters: ProductFilters = Depends(get_filters),
    sort: str = Query("-created_at", description="name, price o created_at; '-' = descendente"),
    params: PageParams = Depends(),
    service: ProductService = Depends(get_service),
):
    return service.search(filters, sort, params)


@router.get("/{product_id}", response_model=ProductOut, summary="Obtener un producto")
def get_product(product_id: int, service: ProductService = Depends(get_service)):
    return service.get(product_id)


@router.patch("/{product_id}", response_model=ProductOut, summary="Modificar parcialmente")
def update_product(product_id: int, data: ProductUpdate,
                   service: ProductService = Depends(get_service)):
    return service.update(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar")
def delete_product(product_id: int, service: ProductService = Depends(get_service)):
    service.delete(product_id)
