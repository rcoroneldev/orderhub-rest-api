"""Errores de dominio y formato estándar de errores (RFC 7807 "Problem Details").

1. Los SERVICES lanzan excepciones de dominio (NotFound, Conflict...), nunca HTTPException.
   Así la lógica de negocio no depende de HTTP y se puede reutilizar y probar sola.
2. Aquí se traducen a respuestas HTTP con un formato único para TODA la API:

{
  "type": "https://orderhub.dev/errors/not-found",
  "title": "Recurso no encontrado",
  "status": 404,
  "detail": "Producto 42 no existe",
  "instance": "/api/v1/products/42"
}
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

ERRORS_BASE = "https://orderhub.dev/errors"


class DomainError(Exception):
    status = 500
    slug = "internal"
    title = "Error interno"

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class NotFound(DomainError):
    status, slug, title = 404, "not-found", "Recurso no encontrado"


class Conflict(DomainError):
    status, slug, title = 409, "conflict", "Conflicto con el estado actual"


class BusinessRuleViolation(DomainError):
    status, slug, title = 422, "business-rule", "Regla de negocio violada"


def problem(request: Request, status: int, slug: str, title: str, detail, **extra) -> JSONResponse:
    body = {"type": f"{ERRORS_BASE}/{slug}", "title": title, "status": status,
            "detail": detail, "instance": request.url.path, **extra}
    return JSONResponse(status_code=status, content=body, media_type="application/problem+json")


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):
        return problem(request, exc.status, exc.slug, exc.title, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = [{"field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]),
                   "message": e["msg"]} for e in exc.errors()]
        return problem(request, 400, "validation", "Datos de entrada inválidos",
                       "Revisa el campo 'errors'", errors=errors)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        # Por ejemplo, 404 de una ruta que no existe o 405 de un método no permitido
        return problem(request, exc.status_code, "http", str(exc.detail), str(exc.detail))
