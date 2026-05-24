# =========================================================
# CAPACIDADES FÍSICAS PRO
# VERSIÓN PROFESIONAL FULL
# Python + Streamlit + PostgreSQL + SQLAlchemy
# =========================================================

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
# CSS PROFESIONAL
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"]{
    font-family: 'Segoe UI';
}

.stApp{
    background: linear-gradient(135deg,#020617,#001845,#001233);
    color:white;
}

/* ===== LOGIN ===== */

.login-wrapper{
    min-height:82vh;
    display:grid;
    grid-template-columns:1.1fr 1fr;
    background:white;
    border-radius:30px;
    overflow:hidden;
    box-shadow:0 25px 80px rgba(0,0,0,.45);
    margin-top:20px;
}

.login-left{
    background: linear-gradient(135deg,#2563eb,#1d4ed8,#38bdf8);
    padding:70px;
    color:white;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}

.login-left h1{
    font-size:58px;
    line-height:1.05;
    font-weight:900;
    color:white;
}

.login-left p{
    color:#dbeafe;
    font-size:18px;
}

.login-right{
    padding:70px;
    background:white;
}

.brand{
    font-size:44px;
    font-weight:900;
    color:#111827;
}

.brand span{
    color:#2563eb;
}

.subtitle{
    color:#64748b;
    margin-bottom:30px;
}

/* ===== INPUTS ===== */

.stTextInput input{
    height:52px;
    border-radius:14px !important;
}

.stNumberInput input{
    border-radius:14px !important;
}

/* ===== BOTONES ===== */

.stButton button{
    width:100%;
    height:52px;
    border-radius:14px;
    border:none;
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    font-weight:800;
}

/* ===== SIDEBAR ===== */

section[data-testid="stSidebar"]{
    background:#020617;
}

/* ===== CARDS ===== */

.card{
    background:#0f172a;
    padding:25px;
    border-radius:20px;
    border:1px solid rgba(255,255,255,.08);
    box-shadow:0 15px 35px rgba(0,0,0,.25);
}

.metric{
    background:#111827;
    padding:20px;
    border-radius:16px;
    text-align:center;
}

.metric h2{
    color:#38bdf8;
    font-size:38px;
}

.metric p{
    color:#cbd5e1;
}

@media(max-width:900px){

.login-wrapper{
grid-template-columns:1fr;
}

.login-left{
display:none;
}

.login-right{
padding:35px;
}

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# POSTGRESQL
# =========================================================

DATABASE_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

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
            SELECT * FROM usuarios
            WHERE usuario=:u
            """), {"u":usuario}).fetchone()

            if existe:
                return False, "Usuario ya existe"

            conn.execute(text("""
            INSERT INTO usuarios(
                nombres,
                usuario,
                password
            )
            VALUES(
                :n,
                :u,
                :p
            )
            """),{
                "n":nombres,
                "u":usuario,
                "p":hash_password(password)
            })

        return True, "Usuario registrado"

    except Exception as e:
        return False, str(e)

def autenticar(usuario, password):

    with engine.begin() as conn:

        data = conn.execute(text("""
        SELECT * FROM usuarios
        WHERE usuario=:u
        AND password=:p
        """),{
            "u":usuario,
            "p":hash_password(password)
        }).fetchone()

        return data

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
    <div class="login-wrapper">

        <div class="login-left">

            <div>
                <p>— Plataforma profesional educativa —</p>
                <h1>Capacidades Físicas PRO</h1>
            </div>

            <div>
                <p><b>Sistema cloud profesional</b></p>
                <p>Evaluación física, estadísticas y gestión escolar avanzada.</p>
            </div>

        </div>

        <div class="login-right">

            <div class="brand">
            Capacidades <span>PRO</span>
            </div>

            <div class="subtitle">
            Ingrese para administrar evaluaciones físicas.
            </div>

    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

    # =====================================================
    # LOGIN
    # =====================================================

    with tab1:

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):

            data = autenticar(usuario, password)

            if data:

                st.session_state.login = True
                st.session_state.usuario = data.usuario
                st.session_state.nombres = data.nombres

                st.rerun()

            else:
                st.error("Usuario o contraseña incorrecta")

    # =====================================================
    # REGISTER
    # =====================================================

    with tab2:

        nombres = st.text_input("Nombres completos")
        nuevo_usuario = st.text_input("Nuevo usuario")
        nuevo_password = st.text_input("Nueva contraseña", type="password")

        if st.button("Crear cuenta"):

            ok, msg = registrar_usuario(
                nombres,
                nuevo_usuario,
                nuevo_password
            )

            if ok:
                st.success(msg)

            else:
                st.error(msg)

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

        st.title("🏃 CAPACIDADES FÍSICAS PRO")

        with engine.begin() as conn:

            total = conn.execute(text("""
            SELECT COUNT(*) FROM evaluaciones
            """)).scalar()

            promedio = conn.execute(text("""
            SELECT AVG(burpee)
            FROM evaluaciones
            """)).scalar()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="metric">
            <h2>{total}</h2>
            <p>Total evaluaciones</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric">
            <h2>{round(promedio or 0,2)}</h2>
            <p>Promedio Burpee</p>
            </div>
            """, unsafe_allow_html=True)

    # =====================================================
    # REGISTRAR
    # =====================================================

    elif menu == "Registrar evaluación":

        st.title("📋 Registrar evaluación")

        with st.form("evaluacion"):

            estudiante = st.text_input("Nombre del estudiante")

            col1, col2 = st.columns(2)

            with col1:
                edad = st.number_input("Edad", 5, 100)

            with col2:
                sexo = st.selectbox(
                    "Sexo",
                    ["Masculino", "Femenino"]
                )

            burpee = st.number_input("Burpee")
            salto = st.number_input("Salto horizontal")
            flexibilidad = st.number_input("Flexibilidad")
            velocidad = st.number_input("Velocidad")

            guardar = st.form_submit_button("Guardar evaluación")

            if guardar:

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
                        :e,
                        :edad,
                        :sexo,
                        :b,
                        :s,
                        :f,
                        :v
                    )
                    """),{
                        "e":estudiante,
                        "edad":edad,
                        "sexo":sexo,
                        "b":burpee,
                        "s":salto,
                        "f":flexibilidad,
                        "v":velocidad
                    })

                st.success("Evaluación guardada")

    # =====================================================
    # RESULTADOS
    # =====================================================

    elif menu == "Resultados":

        st.title("📊 Resultados")

        df = pd.read_sql("""
        SELECT *
        FROM evaluaciones
        ORDER BY fecha DESC
        """, engine)

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode()

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
        SELECT *
        FROM evaluaciones
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

        else:
            st.warning("No existen datos")

# =========================================================
# MAIN
# =========================================================

if st.session_state.login:
    dashboard()
else:
    pantalla_login()