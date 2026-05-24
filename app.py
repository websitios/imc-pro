import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib
import os

# ==========================================================================
# 1. CONFIGURACIÓN DEL SISTEMA E INYECCIÓN VISUAL
# ==========================================================================
st.set_page_config(
    page_title="Capacidades Físicas PRO",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    ruta_css = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==========================================================================
# 2. MOTOR DE CONEXIÓN SEGURO A LA BASE DE DATOS
# ==========================================================================
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

# Inicialización controlada de esquemas institucionales
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

# ==========================================================================
# 3. GESTIÓN CRÍTICA DE ESTADOS DE SESIÓN
# ==========================================================================
if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "modo_login" not in st.session_state:
    st.session_state.modo_login = "ingresar"

# ==========================================================================
# 4. INTERFAZ DE AUTENTICACIÓN (RÉPLICA FIEL DEL BOCETO)
# ==========================================================================
def pantalla_login():
    # Deshabilitar visualmente la sidebar en el login mediante hack CSS limpio
    st.markdown("<style>section[data-testid='stSidebar'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    # Columnas de proporción matemática para encuadrar la tarjeta centralizada
    _, col_central, _ = st.columns([1.1, 1.2, 1.1])

    with col_central:
        # Envoltorio HTML semántico adaptado para el estilo elíptico del CSS
        st.markdown(
            """
            <div class="login-card">
                <h1>Capacidades PRO</h1>
                <p>Sistema Institucional de Evaluación Física Escolar</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # --- SECCIÓN: INICIO DE SESIÓN ---
        if st.session_state.modo_login == "ingresar":
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Ingresar al Sistema</h3>", unsafe_allow_html=True)
            
            usuario = st.text_input("Nombre de Usuario", key="login_usuario", placeholder="Ej. docente_ef")
            password = st.text_input("Contraseña", type="password", key="login_password", placeholder="••••••••")
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                if not usuario.strip() or not password:
                    st.warning("Por favor, introduzca sus credenciales.")
                else:
                    query = text("SELECT usuario FROM usuarios WHERE usuario = :u AND password = :p")
                    with engine.connect() as conn:
                        result = conn.execute(query, {"u": usuario.strip(), "p": hash_password(password)}).fetchone()

                    if result:
                        st.session_state.login = True
                        st.session_state.usuario = usuario.strip()
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos.")

            st.markdown("<p style='text-align: center; font-size: 13px; color: #64748b; margin-top: 25px;'>¿No tienes una cuenta de docente?</p>", unsafe_allow_html=True)
            if st.button("CREAR UNA CUENTA NUEVA", key="btn_ir_registro", use_container_width=True):
                st.session_state.modo_login = "registro"
                st.rerun()

        # --- SECCIÓN: REGISTRO DE NUEVOS DOCENTES ---
        else:
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Registro de Docente</h3>", unsafe_allow_html=True)
            
            nuevo_user = st.text_input("Asignar Usuario", key="nuevo_user", placeholder="Ej. jquispe")
            nuevo_pass = st.text_input("Asignar Contraseña", type="password", key="nuevo_pass", placeholder="Mínimo 6 caracteres")
            
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            
            if st.button("REGISTRAR CUENTA", use_container_width=True):
                if not nuevo_user.strip() or not nuevo_pass:
                    st.warning("Todos los campos son obligatorios.")
                elif len(nuevo_pass) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                            INSERT INTO usuarios(usuario, password)
                            VALUES(:u, :p)
                            """), {
                                "u": nuevo_user.strip(),
                                "p": hash_password(nuevo_pass)
                            })
                        st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
                        st.session_state.modo_login = "ingresar"
                        st.rerun()
                    except Exception:
                        st.error("El nombre de usuario ya se encuentra registrado.")

            st.markdown("<p style='text-align: center; font-size: 13px; color: #64748b; margin-top: 25px;'>¿Ya tienes una cuenta activa?</p>", unsafe_allow_html=True)
            if st.button("VOLVER AL INICIO DE SESIÓN", key="btn_ir_login", use_container_width=True):
                st.session_state.modo_login = "ingresar"
                st.rerun()

# ==========================================================================
# 5. PANEL DE CONTROL INTERNO (POST-LOGIN / DASHBOARD)
# ==========================================================================
def dashboard():
    # Forzar la reaparición de la barra lateral tras autenticarse
    st.markdown("<style>section[data-testid='stSidebar'] { display: block !important; }</style>", unsafe_allow_html=True)
    
    st.sidebar.title("🏃 Menú Principal")
    st.sidebar.info(f"👤 **Docente Activo:**\n{st.session_state.usuario}")

    menu = st.sidebar.radio(
        "Opciones de Navegación",
        ["Dashboard", "Registrar Evaluación", "Resultados", "Estadísticas"]
    )

    st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.08);'><br>", unsafe_allow_html=True)
    if st.sidebar.button("Cerrar Sesión (Salir)", use_container_width=True):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.session_state.modo_login = "ingresar"
        st.rerun()

    # Carga centralizada y segura de los datos una única vez por ciclo
    try:
        df = pd.read_sql("SELECT * FROM evaluaciones ORDER BY fecha DESC", engine)
    except Exception:
        df = pd.DataFrame()

    # --- SUB-PANTALLA: RESUMEN DE MÉTRICAS ---
    if menu == "Dashboard":
        st.title("🏃 Panel de Rendimiento General")
        st.markdown("<p style='color: #64748b;'>Análisis consolidado de aptitud física del alumnado.</p>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        
        if not df.empty:
            c1.metric("Evaluaciones", len(df))
            c2.metric("Prom. Burpee", f"{round(df['burpee'].mean(), 1)} rep")
            c3.metric("Prom. Salto", f"{round(df['salto'].mean(), 1)} cm")
            c4.metric("Prom. Velocidad", f"{round(df['velocidad'].mean(), 1)} s")
        else:
            c1.metric("Evaluaciones", 0)
            c2.metric("Prom. Burpee", "0.0")
            c3.metric("Prom. Salto", "0.0")
            c4.metric("Prom. Velocidad", "0.0")
            st.info("No hay fichas indexadas en este ciclo académico. Registre datos de campo para iniciar.")

    # --- SUB-PANTALLA: ENTRADA DE DATOS DE CAMPO ---
    elif menu == "Registrar Evaluación":
        st.title("📝 Ficha de Registro Técnico")
        st.markdown("<p style='color: #64748b;'>Ingreso de marcas nominales obtenidas en las pruebas físicas.</p>", unsafe_allow_html=True)

        with st.form("form_evaluacion", clear_on_submit=True):
            estudiante = st.text_input("Apellidos y Nombres Completos", placeholder="Ej. Quispe Flores, Alan")

            c1, c2 = st.columns(2)
            edad = c1.number_input("Edad del Estudiante (Años)", min_value=5, max_value=25, value=12)
            sexo = c2.selectbox("Género Biológico", ["Masculino", "Femenino"])

            st.markdown("<h3 style='font-size: 18px; margin-top: 15px;'>Batería de Tests de Aptitud</h3>", unsafe_allow_html=True)
            c3, c4, c5, c6 = st.columns(4)
            burpee = c3.number_input("Burpee (Reps en 1 min)", min_value=0, max_value=100, value=0)
            salto = c4.number_input("Salto Horizontal (cm)", min_value=0, max_value=500, value=0)
            flexibilidad = c5.number_input("Flexibilidad Wells (cm)", min_value=-30, max_value=60, value=0)
            velocidad = c6.number_input("Velocidad 5x10m (s)", min_value=0.0, max_value=60.0, value=0.0, step=0.1)

            st.markdown("<br>", unsafe_allow_html=True)
            guardar = st.form_submit_button("GUARDAR EVALUACIÓN EN REPOSITORIO")

            if guardar:
                if not estudiante.strip():
                    st.error("Error: Debe ingresar de forma obligatoria el nombre del estudiante.")
                else:
                    with engine.begin() as conn:
                        conn.execute(text("""
                        INSERT INTO evaluaciones(estudiante, edad, sexo, burpee, salto, flexibilidad, velocidad, fecha)
                        VALUES(:estudiante, :edad, :sexo, :burpee, :salto, :flexibilidad, :velocidad, :fecha)
                        """), {
                            "estudiante": estudiante.strip(),
                            "edad": edad,
                            "sexo": sexo,
                            "burpee": int(burpee),
                            "salto": int(salto),
                            "flexibilidad": int(flexibilidad),
                            "velocidad": float(velocidad),
                            "fecha": datetime.now()
                        })

                    st.success(f"Éxito: La ficha técnica de {estudiante.strip()} ha sido sincronizada.")
                    st.rerun()

    # --- SUB-PANTALLA: REPOSITORIO Y EXPORTACIÓN ---
    elif menu == "Resultados":
        st.title("📊 Sábana Consolidada de Resultados")
        st.markdown("<p style='color: #64748b;'>Auditoría completa de las marcas físicas registradas por sección.</p>", unsafe_allow_html=True)

        if df.empty:
            st.warning("No existen registros históricos en la base de datos.")
        else:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "EXPORTAR HISTORIAL EN FORMATO EXCEL/CSV",
                csv,
                "registro_evaluaciones_pro.csv",
                "text/csv",
                use_container_width=True
            )

    # --- SUB-PANTALLA: PLOTLY DE RENDIMIENTO ---
    elif menu == "Estadísticas":
        st.title("📈 Análisis Estadístico e Institucional")
        st.markdown("<p style='color: #64748b;'>Interpretación automatizada de percentiles y correlaciones biológicas.</p>", unsafe_allow_html=True)

        if df.empty:
            st.warning("Datos insuficientes para construir diagramas de dispersión.")
        else:
            fig1 = px.histogram(
                df,
                x="burpee",
                color="sexo",
                barmode="group",
                title="Distribución y Frecuencia del Test de Resistencia Anaeróbica (Burpee)"
            )
            fig1.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.scatter(
                df,
                x="salto",
                y="velocidad",
                color="sexo",
                size="edad",
                title="Fuerza Explosiva Inferior (Salto) vs Agilidad Neuromuscular (Velocidad)"
            )
            fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# ==========================================================================
# 6. ENRUTADOR E INICIO PRINCIPAL DE LA APP
# ==========================================================================
if st.session_state.login:
    dashboard()
else:
    pantalla_login()