# =========================================================
# MODELOS / TABLAS
# =========================================================

from sqlalchemy import text
from database.connection import engine

def crear_tablas():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS evaluaciones_imc (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            edad INTEGER NOT NULL,
            sexo VARCHAR(20) NOT NULL,
            peso REAL NOT NULL,
            talla REAL NOT NULL,
            imc REAL NOT NULL,
            diagnostico VARCHAR(100) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """))