import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import hashlib
import os

st.set_page_config(
    page_title="Capacidades Físicas PRO",
    page_icon="🏃",
    layout="wide"
)

def load_css():
    ruta_css = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Conexión Segura a la Base de Datos
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Inicialización Adaptada al modelo real de DBeaver
with engine.begin() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario VARCHAR(100) UNIQUE,
        password VARCHAR(255),
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_fin TIMESTAMP,
        plan VARCHAR(50),
        dias_restantes INT
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

if "modo_login" not in st.session_state:
    st.session_state.modo_login = "ingresar"

def pantalla_login():
    # Ocultar la barra de navegación lateral durante la autenticación
    st.markdown("<style>section[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    _, col_central, _ = st.columns([1.2, 1.4, 1.2])

    with col_central:
        # Se abre el contenedor unificado blanco
        st.markdown('<div class="login-card-unified">', unsafe_allow_html=True)
        
        # Icono de usuario estilizado como la imagen de referencia
        st.markdown("""
        <div class="avatar-container">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <h1>Capacidades PRO</h1>
        <p class="subtitle">Sistema Institucional de Evaluación Física Escolar</p>
        <hr style="border-color: #f1f5f9; margin-bottom: 20px;">
        """, unsafe_allow_html=True)

        # --- SECCIÓN: INICIO DE SESIÓN ---
        if st.session_state.modo_login == "ingresar":
            st.markdown("<h3 style='color: #0f172a; font-size: 18px; margin-bottom: 15px; font-weight:700;'>Ingresar al Sistema</h3>", unsafe_allow_html=True)
            
            usuario = st.text_input("Nombre de Usuario", key="login_usuario", placeholder="Ej. docente_ef")
            password = st.text_input("Contraseña", type="password", key="login_password", placeholder="••••••••")
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                if not usuario.strip() or not password:
                    st.warning("Por favor, introduzca sus credenciales.")
                else:
                    # Buscamos el usuario en la BD
                    query = text("SELECT password FROM usuarios WHERE usuario = :u")
                    with engine.connect() as conn:
                        result = conn.execute(query, {"u": usuario.strip()}).fetchone()

                    if result:
                        bd_password = result[0]
                        # Doble verificación: Acepta tanto el hash SHA-256 como las claves planas antiguas de DBeaver
                        if bd_password == hash_password(password) or bd_password == password:
                            st.session_state.login = True
                            st.session_state.usuario = usuario.strip()
                            st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.error("El usuario no existe en el sistema.")

            st.markdown("<p style='font-size: 12px; color: #64748b; margin-top: 25px; margin-bottom: 5px;'>¿No tienes una cuenta de docente?</p>", unsafe_allow_html=True)
            st.markdown('<div class="btn-secundario">', unsafe_allow_html=True)
            if st.button("CREAR UNA CUENTA NUEVA", key="btn_ir_registro", use_container_width=True):
                st.session_state.modo_login = "registro"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- SECCIÓN: REGISTRO ---
        else:
            st.markdown("<h3 style='color: #0f172a; font-size: 18px; margin-bottom: 15px; font-weight:700;'>Registro de Docente</h3>", unsafe_allow_html=True)
            
            nuevo_user = st.text_input("Asignar Usuario", key="nuevo_user", placeholder="Ej. jquispe")
            nuevo_pass = st.text_input("Asignar Contraseña", type="password", key="nuevo_pass", placeholder="Mínimo 6 caracteres")
            
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if not nuevo_user.strip() or not nuevo_pass:
                    st.warning("Todos los campos son obligatorios.")
                elif len(nuevo_pass) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    try:
                        ahora = datetime.now()
                        fin_prueba = ahora + timedelta(days=15)
                        with engine.begin() as conn:
                            conn.execute(text("""
                            INSERT INTO usuarios(usuario, password, fecha_inicio, fecha_fin, plan, dias_restantes)
                            VALUES(:u, :p, :inicio, :fin, :plan, :dias)
                            """), {
                                "u": nuevo_user.strip(),
                                "p": hash_password(nuevo_pass),
                                "inicio": ahora,
                                "fin": fin_prueba,
                                "plan": "Prueba 15 días",
                                "dias": 15
                            })
                        st.success("¡Cuenta creada con éxito!")
                        st.session_state.modo_login = "ingresar"
                        st.rerun()
                    except Exception:
                        st.error("El nombre de usuario ya se encuentra registrado.")

            st.markdown("<p style='font-size: 12px; color: #64748b; margin-top: 25px; margin-bottom: 5px;'>¿Ya tienes una cuenta activa?</p>", unsafe_allow_html=True)
            st.markdown('<div class="btn-secundario">', unsafe_allow_html=True)
            if st.button("VOLVER AL INICIO DE SESIÓN", key="btn_ir_login", use_container_width=True):
                st.session_state.modo_login = "ingresar"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Se cierra el contenedor principal
        st.markdown('</div>', unsafe_allow_html=True)

# El resto del código correspondiente al dashboard se mantiene igual...
def dashboard():
    st.markdown("<style>section[data-testid='stSidebar'] { display: block !important; }</style>", unsafe_allow_html=True)
    st.sidebar.title("🏃 Menú Principal")
    st.sidebar.success(f"Docente: {st.session_state.usuario}")

    menu = st.sidebar.radio(
        "Opciones de Navegación",
        ["Dashboard", "Registrar Evaluación", "Resultados", "Estadísticas"]
    )

    st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.05);'><br>", unsafe_allow_html=True)
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.session_state.modo_login = "ingresar"
        st.rerun()

    try:
        df = pd.read_sql("SELECT * FROM evaluaciones ORDER BY fecha DESC", engine)
    except Exception:
        df = pd.DataFrame()

    if menu == "Dashboard":
        st.title("🏃 Capacidades Físicas PRO")
        st.markdown("<p style='color: #94a3b8;'>Panel general de rendimiento institucional.</p>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        if not df.empty:
            c1.metric("Evaluaciones", len(df))
            c2.metric("Prom. Burpee", f"{round(df['burpee'].mean(), 2)} rep")
            c3.metric("Prom. Salto", f"{round(df['salto'].mean(), 2)} cm")
            c4.metric("Prom. Velocidad", f"{round(df['velocidad'].mean(), 2)} s")
        else:
            c1.metric("Evaluaciones", 0)
            c2.metric("Prom. Burpee", "0.00")
            c3.metric("Prom. Salto", "0.00")
            c4.metric("Prom. Velocidad", "0.00")
            st.info("No hay datos registrados aún.")

    elif menu == "Registrar Evaluación":
        st.title("📝 Registrar Evaluación Física")
        with st.form("form_evaluacion", clear_on_submit=True):
            estudiante = st.text_input("Nombre Completo del Estudiante", placeholder="Ej. Carlos Mendoza Ramos")
            c1, c2 = st.columns(2)
            edad = c1.number_input("Edad (Años)", min_value=5, max_value=100, value=11)
            sexo = c2.selectbox("Sexo / Género", ["Masculino", "Femenino"])

            st.markdown("<h3 style='font-size: 18px; margin-top: 10px;'>Batería de Tests</h3>", unsafe_allow_html=True)
            c3, c4, c5, c6 = st.columns(4)
            burpee = c3.number_input("Burpee (Repeticiones en 1 min)", min_value=0, value=0)
            salto = c4.number_input("Salto Horizontal (cm)", min_value=0, value=0)
            flexibilidad = c5.number_input("Flexibilidad Wells (cm)", min_value=-50, value=0)
            velocidad = c6.number_input("Velocidad 5x10m (segundos)", min_value=0, value=0)

            guardar = st.form_submit_button("Guardar Evaluación en Base de Datos")
            if guardar:
                if not estudiante.strip():
                    st.error("Error: Debe ingresar el nombre.")
                else:
                    with engine.begin() as conn:
                        conn.execute(text("""
                        INSERT INTO evaluaciones(estudiante, edad, sexo, burpee, salto, flexibilidad, velocidad, fecha)
                        VALUES(:estudiante, :edad, :sexo, :burpee, :salto, :flexibilidad, :velocidad, :fecha)
                        """), {
                            "estudiante": estudiante.strip(), "edad": edad, "sexo": sexo,
                            "burpee": burpee, "salto": salto, "flexibilidad": flexibilidad,
                            "velocidad": velocidad, "fecha": datetime.now()
                        })
                    st.success(f"Ficha de {estudiante.strip()} guardada.")
                    st.rerun()

    elif menu == "Resultados":
        st.title("📊 Registro Histórico")
        if df.empty:
            st.warning("No existen datos.")
        else:
            st.dataframe(df, use_container_width=True)

    elif menu == "Estadísticas":
        st.title("📈 Análisis Estadístico")
        if df.empty:
            st.warning("No hay datos.")
        else:
            fig1 = px.histogram(df, x="burpee", color="sexo", barmode="group", title="Test de Burpee")
            fig1.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

if st.session_state.login:
    dashboard()
else:
    pantalla_login()