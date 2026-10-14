"""Configuración desde variables de entorno o un archivo .env.

Ejemplo:  ORDERHUB_DATABASE_URL=postgresql+psycopg://user:pass@localhost/orderhub
Regla: nunca pongas contraseñas ni claves en el código.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ORDERHUB_")

    app_name: str = "OrderHub API"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./orderhub.db"


settings = Settings()
