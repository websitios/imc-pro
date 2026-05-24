# =====================================================
# QUERIES.PY
# Consultas PostgreSQL IMC PRO
# =====================================================

import pandas as pd

from sqlalchemy import text

from database.connection import engine


# =====================================================
# GUARDAR IMC
# =====================================================

def guardar_imc(
    nombre,
    edad,
    sexo,
    peso,
    talla,
    imc,
    diagnostico
):

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


# =====================================================
# OBTENER DATOS
# =====================================================

def obtener_datos():

    query = """
    SELECT *
    FROM evaluaciones_imc
    ORDER BY id DESC
    """

    return pd.read_sql(
        query,
        engine
    )


# =====================================================
# ELIMINAR REGISTRO
# =====================================================

def eliminar_registro(id_registro):

    with engine.begin() as conn:

        conn.execute(text("""
        DELETE
        FROM evaluaciones_imc
        WHERE id = :id
        """), {

            "id": id_registro
        })


# =====================================================
# FILTRAR POR SEXO
# =====================================================

def filtrar_por_sexo(sexo):

    query = text("""
    SELECT *
    FROM evaluaciones_imc
    WHERE sexo = :sexo
    ORDER BY id DESC
    """)

    return pd.read_sql(
        query,
        engine,
        params={
            "sexo": sexo
        }
    )


# =====================================================
# FILTRAR POR DIAGNÓSTICO
# =====================================================

def filtrar_por_diagnostico(diagnostico):

    query = text("""
    SELECT *
    FROM evaluaciones_imc
    WHERE diagnostico = :dx
    ORDER BY id DESC
    """)

    return pd.read_sql(
        query,
        engine,
        params={
            "dx": diagnostico
        }
    )


# =====================================================
# ESTADÍSTICAS
# =====================================================

def obtener_estadisticas():

    query = """
    SELECT
        COUNT(*) AS total,
        ROUND(AVG(imc)::numeric, 2) AS promedio_imc,
        ROUND(AVG(edad)::numeric, 2) AS promedio_edad
    FROM evaluaciones_imc
    """

    return pd.read_sql(
        query,
        engine
    )