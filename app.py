import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="Capacidades Físicas PRO",
    page_icon="🏃",
    layout="wide"
)

def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

def pantalla_login():
    col1, col2, col3 = st.columns([1.2, 1.1, 1.2])

    with col2:
        st.markdown("""
        <div class="login-card">
            <h1>🏃 Capacidades <span>PRO</span></h1>
            <p>Sistema institucional de evaluación física escolar.</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

        with tab1:
            usuario = st.text_input("Usuario", key="login_usuario")
            password = st.text_input("Contraseña", type="password", key="login_password")

            if st.button("Iniciar sesión"):
                df = pd.read_sql(
                    text("""
                    SELECT * FROM usuarios
                    WHERE usuario=:u AND password=:p
                    """),
                    engine,
                    params={
                        "u": usuario,
                        "p": hash_password(password)
                    }
                )

                if len(df) > 0:
                    st.session_state.login = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

        with tab2:
            nuevo_user = st.text_input("Nuevo usuario", key="nuevo_user")
            nuevo_pass = st.text_input("Nueva contraseña", type="password", key="nuevo_pass")

            if st.button("Crear cuenta"):
                if not nuevo_user or not nuevo_pass:
                    st.warning("Complete todos los campos.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                            INSERT INTO usuarios(usuario, password)
                            VALUES(:u, :p)
                            """), {
                                "u": nuevo_user,
                                "p": hash_password(nuevo_pass)
                            })
                        st.success("Usuario creado correctamente.")
                    except Exception:
                        st.error("El usuario ya existe.")

def dashboard():
    st.sidebar.title("🏃 Menú principal")
    st.sidebar.success(f"Usuario: {st.session_state.usuario}")

    menu = st.sidebar.radio(
        "Opciones",
        ["Dashboard", "Registrar evaluación", "Resultados", "Estadísticas"]
    )

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.rerun()

    if menu == "Dashboard":
        st.title("🏃 Capacidades Físicas PRO")

        df = pd.read_sql("SELECT * FROM evaluaciones", engine)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Evaluaciones", len(df))
        c2.metric("Prom. Burpee", round(df["burpee"].mean(), 2) if not df.empty else 0)
        c3.metric("Prom. Salto", round(df["salto"].mean(), 2) if not df.empty else 0)
        c4.metric("Prom. Velocidad", round(df["velocidad"].mean(), 2) if not df.empty else 0)

    elif menu == "Registrar evaluación":
        st.title("📝 Registrar evaluación física")

        with st.form("form_evaluacion"):
            estudiante = st.text_input("Nombre del estudiante")

            c1, c2 = st.columns(2)
            edad = c1.number_input("Edad", min_value=5, max_value=100, value=10)
            sexo = c2.selectbox("Sexo", ["Masculino", "Femenino"])

            c3, c4, c5, c6 = st.columns(4)
            burpee = c3.number_input("Burpee", min_value=0, value=0)
            salto = c4.number_input("Salto horizontal", min_value=0, value=0)
            flexibilidad = c5.number_input("Flexibilidad", min_value=-50, value=0)
            velocidad = c6.number_input("Velocidad 5x10", min_value=0, value=0)

            guardar = st.form_submit_button("Guardar evaluación")

            if guardar:
                if estudiante.strip() == "":
                    st.error("Ingrese el nombre del estudiante.")
                else:
                    with engine.begin() as conn:
                        conn.execute(text("""
                        INSERT INTO evaluaciones(
                            estudiante, edad, sexo, burpee, salto, flexibilidad, velocidad, fecha
                        )
                        VALUES(
                            :estudiante, :edad, :sexo, :burpee, :salto, :flexibilidad, :velocidad, :fecha
                        )
                        """), {
                            "estudiante": estudiante,
                            "edad": edad,
                            "sexo": sexo,
                            "burpee": burpee,
                            "salto": salto,
                            "flexibilidad": flexibilidad,
                            "velocidad": velocidad,
                            "fecha": datetime.now()
                        })

                    st.success("Evaluación guardada correctamente.")

    elif menu == "Resultados":
        st.title("📊 Resultados")

        df = pd.read_sql("""
        SELECT * FROM evaluaciones
        ORDER BY fecha DESC
        """, engine)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Descargar CSV",
            csv,
            "evaluaciones.csv",
            "text/csv"
        )

    elif menu == "Estadísticas":
        st.title("📈 Estadísticas")

        df = pd.read_sql("SELECT * FROM evaluaciones", engine)

        if df.empty:
            st.warning("No existen datos registrados.")
        else:
            fig1 = px.histogram(
                df,
                x="burpee",
                color="sexo",
                title="Distribución del Test Burpee"
            )
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.scatter(
                df,
                x="salto",
                y="velocidad",
                color="sexo",
                size="edad",
                title="Salto horizontal vs Velocidad"
            )
            st.plotly_chart(fig2, use_container_width=True)

if st.session_state.login:
    dashboard()
else:
    pantalla_login()