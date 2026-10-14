"""
LECCIÓN 1: Tu primera API
=========================

Conceptos:
- Una API REST es un programa que recibe peticiones HTTP y responde datos (casi siempre JSON).
- Una "ruta" (endpoint) = un MÉTODO HTTP + una URL. Ejemplo: GET /
- En FastAPI, cada ruta es una función de Python con un "decorador" encima.

Ejecutar (desde la carpeta lecciones/):
    uvicorn l01_hola:app --reload

    l01_hola  -> nombre del archivo, sin .py
    app       -> la variable FastAPI de abajo
    --reload  -> reinicia el servidor solo cada vez que guardas cambios

Probar:
    http://localhost:8000/          -> tu primera respuesta JSON
    http://localhost:8000/docs      -> documentación interactiva, ¡generada sola!
"""
from fastapi import FastAPI

# 1. Creamos la aplicación. Esta variable es la que busca uvicorn.
app = FastAPI(title="OrderHub - Lección 1")


# 2. @app.get("/") significa:
#    "cuando llegue una petición GET a la URL '/', ejecuta esta función".
@app.get("/")
def inicio():
    # 3. Devuelves un diccionario y FastAPI lo convierte a JSON automáticamente.
    return {"mensaje": "Bienvenido a OrderHub"}


# Una segunda ruta: cada función es un endpoint distinto.
@app.get("/estado")
def estado():
    return {"servicio": "orderhub", "activo": True, "version": 1}


# RETO: crea GET /tienda que devuelva el nombre de tu tienda y su moneda (por ejemplo, "PEN").
# Luego búscala en /docs y pruébala con el botón "Try it out".
