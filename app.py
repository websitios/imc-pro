import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import plotly.express as px

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Capacidades Físicas PRO",
    layout="wide"
)

# =========================================================
# DATABASE
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
        usuario TEXT UNIQUE,
        password TEXT,
        fecha_inicio TIMESTAMP,
        fecha_fin TIMESTAMP,
        plan TEXT,
        dias_restantes INTEGER
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id SERIAL PRIMARY KEY,
        estudiante TEXT,
        edad INTEGER,
        sexo TEXT,
        burpee INTEGER,
        salto REAL,
        flexibilidad REAL,
        velocidad REAL,
        fecha TIMESTAMP
    )
    """))

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
background:#111827;
}

h1,h2,h3{
color:#38bdf8;
}

.stButton>button{
background:linear-gradient(90deg,#06b6d4,#9333ea);
color:white;
border:none;
border-radius:10px;
padding:10px;
font-weight:bold;
}

.box{
background:#111827;
padding:20px;
border-radius:15px;
border:1px solid #334155;
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION
# =========================================================

if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN
# =========================================================

def login():

    st.title("🏃 CAPACIDADES FÍSICAS PRO")

    menu = st.tabs(["Ingresar","Registrarse"])

    # LOGIN
    with menu[0]:

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):

            with engine.begin() as conn:

                result = conn.execute(text("""
                SELECT * FROM usuarios
                WHERE usuario=:u AND password=:p
                """), {
                    "u":usuario,
                    "p":password
                }).fetchone()

            if result:

                st.session_state.login = True
                st.session_state.usuario = usuario
                st.rerun()

            else:
                st.error("Usuario incorrecto")

    # REGISTRO
    with menu[1]:

        nuevo_usuario = st.text_input("Nuevo usuario")
        nuevo_password = st.text_input("Nueva contraseña", type="password")

        if st.button("Crear cuenta"):

            inicio = datetime.now()
            fin = inicio + timedelta(days=15)

            try:

                with engine.begin() as conn:

                    conn.execute(text("""
                    INSERT INTO usuarios
                    (usuario,password,fecha_inicio,fecha_fin,plan,dias_restantes)
                    VALUES
                    (:u,:p,:i,:f,:pl,:d)
                    """),{
                        "u":nuevo_usuario,
                        "p":nuevo_password,
                        "i":inicio,
                        "f":fin,
                        "pl":"Prueba 15 días",
                        "d":15
                    })

                st.success("Cuenta creada")

            except:
                st.error("Usuario ya existe")

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
            "Estadísticas",
            "Suscripción"
        ]
    )

    # =====================================================
    # DASHBOARD
    # =====================================================

    if menu == "Dashboard":

        st.title("📊 Dashboard")

        with engine.begin() as conn:

            total = conn.execute(text("""
            SELECT COUNT(*) FROM evaluaciones
            """)).scalar()

        col1,col2,col3 = st.columns(3)

        col1.metric("Evaluaciones", total)
        col2.metric("Usuarios", "Online")
        col3.metric("Sistema", "Activo")

    # =====================================================
    # REGISTRO
    # =====================================================

    elif menu == "Registrar evaluación":

        st.title("📝 Registrar evaluación")

        estudiante = st.text_input("Estudiante")
        edad = st.number_input("Edad",1,100)
        sexo = st.selectbox("Sexo",["Masculino","Femenino"])

        burpee = st.number_input("Test Burpee")
        salto = st.number_input("Salto Horizontal")
        flexibilidad = st.number_input("Sit and Reach")
        velocidad = st.number_input("Velocidad 5x10")

        if st.button("Guardar evaluación"):

            with engine.begin() as conn:

                conn.execute(text("""
                INSERT INTO evaluaciones
                (estudiante,edad,sexo,burpee,salto,flexibilidad,velocidad,fecha)
                VALUES
                (:e,:ed,:s,:b,:sa,:f,:v,:fe)
                """),{
                    "e":estudiante,
                    "ed":edad,
                    "s":sexo,
                    "b":burpee,
                    "sa":salto,
                    "f":flexibilidad,
                    "v":velocidad,
                    "fe":datetime.now()
                })

            st.success("Evaluación guardada")

    # =====================================================
    # RESULTADOS
    # =====================================================

    elif menu == "Resultados":

        st.title("📋 Resultados")

        with engine.begin() as conn:

            df = pd.read_sql("""
            SELECT * FROM evaluaciones
            ORDER BY id DESC
            """, conn)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode()

        st.download_button(
            "Descargar CSV",
            csv,
            "evaluaciones.csv",
            "text/csv"
        )

    # =====================================================
    # ESTADISTICAS
    # =====================================================

    elif menu == "Estadísticas":

        st.title("📈 Estadísticas")

        with engine.begin() as conn:

            df = pd.read_sql("""
            SELECT * FROM evaluaciones
            """, conn)

        if not df.empty:

            fig = px.histogram(
                df,
                x="burpee",
                title="Distribución Test Burpee"
            )

            st.plotly_chart(fig, use_container_width=True)

    # =====================================================
    # SUSCRIPCION
    # =====================================================

    elif menu == "Suscripción":

        st.title("💳 Planes")

        col1,col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class='box'>
            <h2>Plan Mensual</h2>
            <h1>S/ 35</h1>
            <p>30 días</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='box'>
            <h2>Plan Anual</h2>
            <h1>S/ 360</h1>
            <p>365 días</p>
            </div>
            """, unsafe_allow_html=True)

        metodo = st.radio(
            "Método pago",
            ["Yape","Tarjeta"]
        )

        st.text_input("Código operación")

        st.file_uploader(
            "Subir captura",
            type=["png","jpg","jpeg"]
        )

        if st.button("Enviar pago"):
            st.success("Pago enviado para validación")

    # =====================================================
    # LOGOUT
    # =====================================================

    if st.sidebar.button("Cerrar sesión"):

        st.session_state.login = False
        st.rerun()

# =========================================================
# MAIN
# =========================================================

if st.session_state.login:
    dashboard()
else:
    login()