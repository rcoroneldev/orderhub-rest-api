# OrderHub API: arquitectura

## 1. Propósito

API RESTful para una tienda en línea: gestiona **productos**, **clientes** y **pedidos**.
Es un proyecto de aprendizaje que se construye por etapas, desde lo más básico hasta un
servicio listo para producción.

## 2. Modelo de datos

```
CUSTOMER 1 ──── * ORDER 1 ──── * ORDER_ITEM * ──── 1 PRODUCT
```

| Entidad | Campos principales |
|---|---|
| `Product` | id, sku (único), name, description, price, stock, is_active, created_at, updated_at |
| `Customer` (etapa 4) | id, email (único), full_name, created_at |
| `Order` (etapa 4) | id, customer_id, status, total, created_at |
| `OrderItem` (etapa 4) | id, order_id, product_id, quantity, unit_price |

Decisiones:
- `OrderItem.unit_price` **copia** el precio al momento de la compra: si el producto
  cambia de precio, los pedidos antiguos no cambian.
- El dinero usa `Decimal` / `Numeric(10, 2)`, nunca `float`.

## 3. Ciclo de vida de un pedido (etapa 4)

```
pending ──pay──► paid ──ship──► shipped ──deliver──► delivered
   │               │
   └────cancel─────┴──► cancelled   (devuelve el stock)
```

Una transición no permitida responde `409 Conflict`.

## 4. Arquitectura en capas

```
Petición HTTP
     │
     ▼
 Router       → HTTP: rutas, validación de entrada con Pydantic, códigos de estado
     │
     ▼
 Service      → reglas de negocio; no conoce HTTP; lanza errores de dominio
     │
     ▼
 Repository   → acceso a datos con SQLAlchemy; lo único que escribe SQL
     │
     ▼
 SQLite (desarrollo y tests)  /  PostgreSQL (etapa 6)
```

```
app/
  main.py                     # create_app(): registra routers y manejadores de errores
  core/config.py              # configuración por variables de entorno (ORDERHUB_*)
  core/errors.py              # errores de dominio → RFC 7807
  db/session.py               # engine, sesión y dependencia get_db
  common/pagination.py        # Page[T], PageParams, ordenamiento con lista blanca
  modules/
    products/                 # router, service, repository, schemas, models
    customers/                # etapa 4
    orders/                   # etapa 4
    auth/                     # etapa 5
```

## 5. Convenciones de la API

| Tema | Decisión |
|---|---|
| Versionado | En la URL: `/api/v1` |
| Recursos | Sustantivos en plural (`/products`), JSON en `snake_case` |
| Crear | `201 Created` + cabecera `Location` |
| Modificar | `PATCH` parcial (`exclude_unset`); el SKU no se modifica |
| Borrar | `204 No Content` |
| Acciones de estado | `POST /orders/{id}/pay` (transiciones explícitas) |
| Errores | RFC 7807, `application/problem+json` |
| Validación | `400` con `errors: [{field, message}]` |
| Reglas de negocio | `409` (conflicto de estado) o `422` (regla violada) |
| Paginación | `?page=&size=` → `{items, total, page, size, pages}` |
| Orden | `?sort=-price` (lista blanca de campos) |
| Dinero | Texto decimal exacto en JSON: `"39.90"` |
| Fechas | ISO 8601 en UTC |

## 6. Decisiones de arquitectura (ADRs)

**ADR-001: Monolito modular.** Un solo servicio con módulos por área de negocio.
Suficiente para este tamaño y mucho más simple de operar que microservicios.

**ADR-002: SQLAlchemy síncrono.** Más fácil de entender y depurar. FastAPI ejecuta los
endpoints `def` en un pool de hilos, así que no bloquean el servidor.

**ADR-003: SQLite en desarrollo y tests, PostgreSQL en producción.** La capa de
repositorio aísla la diferencia; solo cambia `ORDERHUB_DATABASE_URL`.

**ADR-004: Errores de dominio en los services.** Los services no lanzan `HTTPException`.
Así la lógica de negocio se puede reutilizar (un service llama a otro) y probar sin HTTP.

**ADR-005: Errores RFC 7807.** Un formato único simplifica la vida de los clientes de la API.

**ADR-006: Tests de contrato estables.** `tests/test_products.py` es idéntico en las
etapas 1, 2 y 3: demuestra que refactorizar la estructura interna no rompe la API.

## 7. Etapas

| Etapa | Contenido | Tag |
|---|---|---|
| 0 | Lecciones 1 a 9 (`lecciones/`) | — |
| 1 | CRUD de productos en un archivo, en memoria | `etapa-1` |
| 2 | SQLite + SQLAlchemy | `etapa-2` |
| 3 | Arquitectura en capas + errores RFC 7807 | `etapa-3` |
| 4 | Clientes y pedidos: stock, totales, máquina de estados | pendiente |
| 5 | Registro, login JWT, roles `customer` y `admin` | pendiente |
| 6 | Docker, PostgreSQL, Alembic, logs estructurados | pendiente |
