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
    try:
        with open("style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css()

# Conexión Segura a la Base de Datos
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Inicialización de la Base de Datos (Estructura Institucional)
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

# Manejo de Estados de la Sesión
if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "modo_login" not in st.session_state:
    st.session_state.modo_login = "ingresar"

def pantalla_login():
    # Centrado perfecto de la tarjeta de autenticación
    _, col_central, _ = st.columns([1, 1.4, 1])

    with col_central:
        with st.container():
            # Encabezado HTML integrado con el CSS Premium
            st.markdown("""
            <div class="login-card">
                <h1>🏃 Capacidades <span style="color: #38bdf8;">PRO</span></h1>
                <p style="color: #94a3b8; font-size: 14px; margin-top: -5px;">
                    Sistema Institucional de Evaluación Física Escolar
                </p>
                <hr style="border-color: rgba(255,255,255,0.05); margin: 20px 0;">
            </div>
            """, unsafe_allow_html=True)

            # --- MODO: INICIAR SESIÓN ---
            if st.session_state.modo_login == "ingresar":
                st.markdown("<h3 style='text-align: center; font-size: 20px; margin-bottom: 15px;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
                
                usuario = st.text_input("Nombre de Usuario", key="login_usuario", placeholder="Ej. docente_ef")
                password = st.text_input("Contraseña", type="password", key="login_password", placeholder="••••••••")
                
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                
                if st.button("Ingresar al Sistema", use_container_width=True):
                    if not usuario.strip() or not password:
                        st.warning("Por favor, introduzca sus credenciales.")
                    else:
                        # Consulta parametrizada segura contra inyecciones SQL
                        query = text("SELECT usuario FROM usuarios WHERE usuario = :u AND password = :p")
                        with engine.connect() as conn:
                            result = conn.execute(query, {"u": usuario.strip(), "p": hash_password(password)}).fetchone()

                        if result:
                            st.session_state.login = True
                            st.session_state.usuario = usuario.strip()
                            st.rerun()
                        else:
                            st.error("Usuario o contraseña incorrectos.")

                # Switch dinámico de pantalla sin pestañas toscas
                st.markdown("<p style='text-align: center; font-size: 13px; color: #64748b; margin-top: 25px;'>¿No tienes una cuenta de docente?</p>", unsafe_allow_html=True)
                if st.button("Crear una cuenta nueva", key="btn_ir_registro", use_container_width=True):
                    st.session_state.modo_login = "registro"
                    st.rerun()

            # --- MODO: REGISTRO ---
            else:
                st.markdown("<h3 style='text-align: center; font-size: 20px; margin-bottom: 15px;'>Registro de Docente</h3>", unsafe_allow_html=True)
                
                nuevo_user = st.text_input("Asignar Usuario", key="nuevo_user", placeholder="Ej. jquispe")
                nuevo_pass = st.text_input("Asignar Contraseña", type="password", key="nuevo_pass", placeholder="Mínimo 6 caracteres")
                
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                
                if st.button("Registrar Cuenta", use_container_width=True):
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
                if st.button("Volver al Inicio de Sesión", key="btn_ir_login", use_container_width=True):
                    st.session_state.modo_login = "ingresar"
                    st.rerun()

def dashboard():
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

    # Carga centralizada y segura de los datos una única vez por ciclo
    try:
        df = pd.read_sql("SELECT * FROM evaluaciones ORDER BY fecha DESC", engine)
    except Exception:
        df = pd.DataFrame()

    # --- PANTALLA: DASHBOARD ---
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
            st.info("No hay datos registrados aún en este período académico. Dirígete a la sección de registro.")

    # --- PANTALLA: REGISTRAR EVALUACIÓN ---
    elif menu == "Registrar Evaluación":
        st.title("📝 Registrar Evaluación Física")
        st.markdown("<p style='color: #94a3b8;'>Ingrese los resultados obtenidos en las pruebas de campo.</p>", unsafe_allow_html=True)

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

            st.markdown("<br>", unsafe_allow_html=True)
            guardar = st.form_submit_button("Guardar Evaluación en Base de Datos")

            if guardar:
                if not estudiante.strip():
                    st.error("Error: Debe ingresar de forma obligatoria el nombre del estudiante.")
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
                            "estudiante": estudiante.strip(),
                            "edad": edad,
                            "sexo": sexo,
                            "burpee": burpee,
                            "salto": salto,
                            "flexibilidad": flexibilidad,
                            "velocidad": velocidad,
                            "fecha": datetime.now()
                        })

                    st.success(f"Éxito: La ficha de evaluación de {estudiante.strip()} ha sido archivada.")
                    st.rerun()

    # --- PANTALLA: RESULTADOS ---
    elif menu == "Resultados":
        st.title("📊 Registro Histórico de Resultados")
        st.markdown("<p style='color: #94a3b8;'>Matriz completa de datos registrados. Permite auditoría y exportaciones oficiales.</p>", unsafe_allow_html=True)

        if df.empty:
            st.warning("No existen datos indexados en la base de datos.")
        else:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Exportar Registro en formato CSV",
                csv,
                "registro_evaluaciones_pro.csv",
                "text/csv",
                use_container_width=True
            )

    # --- PANTALLA: ESTADÍSTICAS ---
    elif menu == "Estadísticas":
        st.title("📈 Análisis Estadístico Avanzado")
        st.markdown("<p style='color: #94a3b8;'>Distribuciones de rendimiento y correlaciones por grupo biológico.</p>", unsafe_allow_html=True)

        if df.empty:
            st.warning("No existen datos suficientes para estructurar las métricas visuales.")
        else:
            fig1 = px.histogram(
                df,
                x="burpee",
                color="sexo",
                barmode="group",
                title="Distribución y Frecuencia del Test de Burpee"
            )
            fig1.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.scatter(
                df,
                x="salto",
                y="velocidad",
                color="sexo",
                size="edad",
                title="Correlación: Fuerza Explosiva Tren Inferior (Salto) vs Velocidad Agilidad"
            )
            fig2.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# Enrutador de Acceso Primario
if st.session_state.login:
    dashboard()
else:
    pantalla_login()