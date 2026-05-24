import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Capacidades Físicas PRO",
    page_icon="🏃",
    layout="wide"
)

# =========================================================
# CSS EXTERNO
# =========================================================

def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =========================================================
# BASE DE DATOS
# =========================================================

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

# =========================================================
# CREAR TABLAS
# =========================================================

with engine.begin() as conn:

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(100) UNIQUE,
        password VARCHAR(255)
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id SERIAL PRIMARY KEY,
        estudiante VARCHAR(200),
        edad INT,
        sexo VARCHAR(50),
        burpee INT,
        salto INT,
        flexibilidad INT,
        velocidad INT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))

# =========================================================
# HASH PASSWORD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# SESSION
# =========================================================

if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN
# =========================================================

def pantalla_login():

    st.markdown("""
    <div class="login-container">

        <div class="login-left">
            <div class="overlay">
                <h1>CAPACIDADES FÍSICAS PRO</h1>
                <p>Sistema institucional de evaluación física.</p>
                <p>Plataforma cloud profesional.</p>
            </div>
        </div>

        <div class="login-right">

    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    # LOGIN
    with tab1:

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):

            query = text("""
            SELECT * FROM usuarios
            WHERE usuario=:u AND password=:p
            """)

            df = pd.read_sql(
                query,
                engine,
                params={
                    "u": usuario,
                    "p": hash_password(password)
                }
            )

            if len(df) > 0:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    # REGISTRO
    with tab2:

        nuevo_user = st.text_input("Nuevo usuario")
        nuevo_pass = st.text_input("Nueva contraseña", type="password")

        if st.button("Crear cuenta"):

            with engine.begin() as conn:
                conn.execute(text("""
                INSERT INTO usuarios(usuario,password)
                VALUES(:u,:p)
                """), {
                    "u": nuevo_user,
                    "p": hash_password(nuevo_pass)
                })

            st.success("Usuario creado")

    st.markdown("</div></div>", unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================

def dashboard():

    st.sidebar.title("🏃 Menú")

    menu = st.sidebar.radio(
        "Opciones",
        [
            "Dashboard",
            "Registrar evaluación",
            "Resultados",
            "Estadísticas"
        ]
    )

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.login = False
        st.rerun()

    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "Dashboard":

        st.title("🏃 Capacidades Físicas PRO")

        total = pd.read_sql(
            "SELECT COUNT(*) as total FROM evaluaciones",
            engine
        )

        st.metric(
            "Evaluaciones registradas",
            total["total"][0]
        )

    # =====================================================
    # REGISTRO
    # =====================================================

    elif menu == "Registrar evaluación":

        st.title("📝 Registrar Evaluación")

        estudiante = st.text_input("Nombre del estudiante")
        edad = st.number_input("Edad", 5, 100)
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])

        burpee = st.number_input("Burpee")
        salto = st.number_input("Salto")
        flexibilidad = st.number_input("Flexibilidad")
        velocidad = st.number_input("Velocidad")

        if st.button("Guardar evaluación"):

            with engine.begin() as conn:

                conn.execute(text("""
                INSERT INTO evaluaciones(
                    estudiante,
                    edad,
                    sexo,
                    burpee,
                    salto,
                    flexibilidad,
                    velocidad
                )
                VALUES(
                    :estudiante,
                    :edad,
                    :sexo,
                    :burpee,
                    :salto,
                    :flexibilidad,
                    :velocidad
                )
                """), {
                    "estudiante": estudiante,
                    "edad": edad,
                    "sexo": sexo,
                    "burpee": burpee,
                    "salto": salto,
                    "flexibilidad": flexibilidad,
                    "velocidad": velocidad
                })

            st.success("Evaluación guardada")

    # =====================================================
    # RESULTADOS
    # =====================================================

    elif menu == "Resultados":

        st.title("📊 Resultados")

        df = pd.read_sql("""
        SELECT * FROM evaluaciones
        ORDER BY id DESC
        """, engine)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "evaluaciones.csv",
            "text/csv"
        )

    # =====================================================
    # ESTADÍSTICAS
    # =====================================================

    elif menu == "Estadísticas":

        st.title("📈 Estadísticas")

        df = pd.read_sql("""
        SELECT * FROM evaluaciones
        """, engine)

        if len(df) > 0:

            fig = px.histogram(
                df,
                x="burpee",
                color="sexo",
                title="Distribución Burpee"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            fig2 = px.scatter(
                df,
                x="salto",
                y="velocidad",
                color="sexo",
                size="edad",
                title="Salto vs Velocidad"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

# =========================================================
# MAIN
# =========================================================

if st.session_state.login:
    dashboard()
else:
    pantalla_login()