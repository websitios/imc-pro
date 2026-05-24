# =========================================================
# CAPACIDADES FÍSICAS PRO
# Versión profesional Streamlit + PostgreSQL Render
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Capacidades Físicas PRO",
    page_icon="🏃",
    layout="wide"
)

DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>
.stApp{
    background: linear-gradient(135deg,#020617,#001233);
    color:white;
}
section[data-testid="stSidebar"]{
    background:#0f172a;
}
.login-card{
    background:#ffffff;
    padding:45px;
    border-radius:28px;
    box-shadow:0 25px 80px rgba(0,0,0,.35);
    color:#111827;
}
.login-title{
    font-size:42px;
    font-weight:900;
    color:#111827;
}
.login-title span{
    color:#2563eb;
}
.login-sub{
    color:#64748b;
    margin-bottom:25px;
}
.stTextInput input{
    border-radius:12px !important;
    height:50px;
}
.stButton button{
    background:linear-gradient(90deg,#2563eb,#7c3aed);
    color:white;
    border:none;
    border-radius:12px;
    font-weight:800;
    height:48px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TABLAS
# =========================================================

with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id SERIAL PRIMARY KEY,
        nombres TEXT,
        usuario TEXT UNIQUE,
        password TEXT,
        rol TEXT DEFAULT 'Docente',
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS evaluaciones(
        id SERIAL PRIMARY KEY,
        estudiante TEXT,
        edad INTEGER,
        sexo TEXT,
        burpee INTEGER,
        salto INTEGER,
        flexibilidad INTEGER,
        velocidad INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """))

# =========================================================
# FUNCIONES
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar_usuario(nombres, usuario, password):
    try:
        with engine.begin() as conn:
            existe = conn.execute(text("""
                SELECT id FROM usuarios WHERE usuario=:usuario
            """), {"usuario": usuario}).fetchone()

            if existe:
                return False, "El usuario ya existe."

            conn.execute(text("""
                INSERT INTO usuarios(nombres, usuario, password)
                VALUES(:nombres, :usuario, :password)
            """), {
                "nombres": nombres,
                "usuario": usuario,
                "password": hash_password(password)
            })

        return True, "Usuario registrado correctamente."
    except Exception as e:
        return False, str(e)

def autenticar(usuario, password):
    with engine.begin() as conn:
        data = conn.execute(text("""
            SELECT * FROM usuarios
            WHERE usuario=:usuario AND password=:password
        """), {
            "usuario": usuario,
            "password": hash_password(password)
        }).fetchone()

    return data

# =========================================================
# SESSION
# =========================================================

if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN CORREGIDO
# =========================================================

def pantalla_login():
    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-title">Capacidades <span>PRO</span></div>
            <div class="login-sub">
                Sistema profesional institucional para evaluación de capacidades físicas escolares.
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

        with tab1:
            usuario = st.text_input("Usuario", key="login_user")
            password = st.text_input("Contraseña", type="password", key="login_pass")

            if st.button("Iniciar sesión"):
                data = autenticar(usuario, password)

                if data:
                    st.session_state.login = True
                    st.session_state.usuario = data.usuario
                    st.session_state.nombres = data.nombres
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrecta.")

        with tab2:
            nombres = st.text_input("Nombres completos", key="reg_nombres")
            nuevo_usuario = st.text_input("Nuevo usuario", key="reg_usuario")
            nuevo_password = st.text_input("Nueva contraseña", type="password", key="reg_password")

            if st.button("Crear cuenta"):
                if not nombres or not nuevo_usuario or not nuevo_password:
                    st.warning("Complete todos los campos.")
                else:
                    ok, msg = registrar_usuario(nombres, nuevo_usuario, nuevo_password)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# =========================================================
# DASHBOARD
# =========================================================

def dashboard():
    st.sidebar.title("🏃 Menú")

    menu = st.sidebar.radio(
        "Opciones",
        ["Dashboard", "Registrar evaluación", "Resultados", "Estadísticas"]
    )

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.login = False
        st.rerun()

    if menu == "Dashboard":
        st.title("🏃 Capacidades Físicas PRO")
        st.write(f"Usuario activo: **{st.session_state.nombres}**")

        df = pd.read_sql("SELECT * FROM evaluaciones", engine)

        c1, c2, c3 = st.columns(3)
        c1.metric("Total evaluaciones", len(df))
        c2.metric("Promedio Burpee", round(df["burpee"].mean(), 2) if not df.empty else 0)
        c3.metric("Promedio Salto", round(df["salto"].mean(), 2) if not df.empty else 0)

    elif menu == "Registrar evaluación":
        st.title("📋 Registrar evaluación")

        with st.form("form_eval"):
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
                title="Distribución del Test de Burpee"
            )
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.scatter(
                df,
                x="salto",
                y="velocidad",
                color="sexo",
                size="edad",
                title="Relación entre salto horizontal y velocidad"
            )
            st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# MAIN
# =========================================================

if st.session_state.login:
    dashboard()
else:
    pantalla_login()