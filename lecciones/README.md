# FastAPI desde cero

Nueve lecciones cortas. Cada archivo se ejecuta solo e introduce **un** concepto nuevo.
Todas usan productos y pedidos, así que al terminar entenderás cada pieza de OrderHub (`../app`).

## Preparación (una sola vez, desde la raíz del repositorio)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd lecciones
```

## Cómo estudiar cada lección

1. Lee el comentario inicial del archivo: explica el concepto y qué probar.
2. Ejecuta `uvicorn <archivo_sin_.py>:app --reload` y abre http://localhost:8000/docs
3. Haz las pruebas que indica el comentario, **incluidas las que fallan a propósito**.
4. Resuelve el RETO del final antes de pasar a la siguiente.

| # | Archivo | Concepto | Comando |
|---|---|---|---|
| 1 | `l01_hola.py` | Primera API, rutas, `/docs` | `uvicorn l01_hola:app --reload` |
| 2 | `l02_parametros_ruta.py` | Parámetros de ruta, tipos, Enum | `uvicorn l02_parametros_ruta:app --reload` |
| 3 | `l03_parametros_query.py` | Filtros y paginación con query params | `uvicorn l03_parametros_query:app --reload` |
| 4 | `l04_body_pydantic.py` | Recibir JSON y validarlo con Pydantic; dinero con `Decimal` | `uvicorn l04_body_pydantic:app --reload` |
| 5 | `l05_respuestas.py` | `response_model` y códigos de estado | `uvicorn l05_respuestas:app --reload` |
| 6 | `l06_crud.py` | CRUD completo, 404/409, PUT vs PATCH | `uvicorn l06_crud:app --reload` |
| 7 | `l07_dependencias.py` | `Depends`, API keys, 401 vs 403 | `uvicorn l07_dependencias:app --reload` |
| 8 | `l08_base_datos.py` | SQLite + SQLAlchemy | `uvicorn l08_base_datos:app --reload` |
| 9 | `test_l09_tests.py` | Tests automáticos con pytest | `pytest -v test_l09_tests.py` |

Las lecciones usan nombres en español (`nombre`, `precio`) para que se lean fácil.
El proyecto principal usa nombres en inglés (`name`, `price`), que es la convención
habitual en APIs profesionales.

## Después de la lección 9

Vuelve a la raíz del repositorio y sigue las **etapas** del README principal.
