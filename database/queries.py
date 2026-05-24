# =========================================================
# CONSULTAS SQL
# =========================================================

import pandas as pd
from sqlalchemy import text
from database.connection import engine

def guardar_imc(nombre, edad, sexo, peso, talla, imc, diagnostico):
    with engine.begin() as conn:
        conn.execute(text("""
        INSERT INTO evaluaciones_imc (
            nombre,
            edad,
            sexo,
            peso,
            talla,
            imc,
            diagnostico
        )
        VALUES (
            :nombre,
            :edad,
            :sexo,
            :peso,
            :talla,
            :imc,
            :diagnostico
        )
        """), {
            "nombre": nombre,
            "edad": edad,
            "sexo": sexo,
            "peso": peso,
            "talla": talla,
            "imc": imc,
            "diagnostico": diagnostico
        })


def obtener_datos():
    return pd.read_sql(
        """
        SELECT *
        FROM evaluaciones_imc
        ORDER BY fecha DESC
        """,
        engine
    )