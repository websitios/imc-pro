# =====================================================
# AUTH.PY
# Login profesional PostgreSQL + bcrypt
# =====================================================

import bcrypt
import pandas as pd

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.connection import engine


# =====================================================
# HASH PASSWORD
# =====================================================

def hash_password(password: str) -> str:

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


# =====================================================
# VERIFY PASSWORD
# =====================================================

def verify_password(
    password: str,
    hashed: str
) -> bool:

    try:

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )

    except Exception:

        return False


# =====================================================
# REGISTER USER
# =====================================================

def registrar_usuario(
    usuario: str,
    password: str
):

    try:

        usuario = usuario.strip()

        # VALIDACIONES
        if len(usuario) < 3:

            return (
                False,
                "El usuario debe tener mínimo 3 caracteres."
            )

        if len(password) < 4:

            return (
                False,
                "La contraseña es demasiado corta."
            )

        # VERIFICAR SI EXISTE
        query = text("""
        SELECT id
        FROM usuarios
        WHERE usuario = :u
        """)

        df = pd.read_sql(
            query,
            engine,
            params={
                "u": usuario
            }
        )

        if not df.empty:

            return (
                False,
                "El usuario ya existe."
            )

        # HASH PASSWORD
        hashed = hash_password(password)

        # INSERTAR
        with engine.begin() as conn:

            conn.execute(text("""
            INSERT INTO usuarios (
                usuario,
                password
            )
            VALUES (
                :u,
                :p
            )
            """), {

                "u": usuario,
                "p": hashed
            })

        return (
            True,
            "Usuario registrado correctamente."
        )

    except SQLAlchemyError:

        return (
            False,
            "Error de conexión con PostgreSQL."
        )

    except Exception as e:

        return (
            False,
            str(e)
        )


# =====================================================
# LOGIN USER
# =====================================================

def login_usuario(
    usuario: str,
    password: str
) -> bool:

    try:

        query = text("""
        SELECT *
        FROM usuarios
        WHERE usuario = :u
        """)

        df = pd.read_sql(
            query,
            engine,
            params={
                "u": usuario
            }
        )

        # USUARIO NO EXISTE
        if df.empty:

            return False

        hashed = df.iloc[0]["password"]

        return verify_password(
            password,
            hashed
        )

    except SQLAlchemyError:

        return False

    except Exception:

        return False


# =====================================================
# GET USER
# =====================================================

def obtener_usuario(
    usuario: str
):

    try:

        query = text("""
        SELECT
            id,
            usuario,
            rol,
            fecha
        FROM usuarios
        WHERE usuario = :u
        """)

        df = pd.read_sql(
            query,
            engine,
            params={
                "u": usuario
            }
        )

        if df.empty:

            return None

        return df.iloc[0].to_dict()

    except Exception:

        return None