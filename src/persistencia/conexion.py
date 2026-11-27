import os
from dotenv import load_dotenv
import pymysql
import sqlite3

load_dotenv()


def obtener_motor() -> str:
    return os.getenv("DB_ENGINE", "sqlite").strip().lower()


def marcador_parametro() -> str:
    """Devuelve el marcador de parámetros SQL según el motor ("?" en SQLite, "%s" en MySQL)."""
    return "?" if obtener_motor() == "sqlite" else "%s"


def abrir_conexion():
    motor = obtener_motor()

    if motor == "sqlite":
        ruta_bd = os.getenv("DB_NAME", "ecotech.db")
        return sqlite3.connect(ruta_bd)

    if motor == "mysql":
        puerto_texto = os.getenv("DB_PORT", "3306")
        try:
            puerto = int(puerto_texto)
        except ValueError as error:
            raise ValueError(f"El puerto de MySQL '{puerto_texto}' no es válido.") from error

        return pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=puerto,
            user=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "ecotech"),
            charset="utf8mb4",
        )

    raise ValueError(f"Motor de base de datos no soportado: {motor}")