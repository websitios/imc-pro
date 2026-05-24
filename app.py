# =====================================================
# IMC PRO - APP.PY
# Estructura modular profesional
# =====================================================

import streamlit as st
import plotly.express as px

from database.models import crear_tablas
from database.auth import registrar_usuario, login_usuario
from database.queries import guardar_imc, obtener_datos


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="IMC PRO",
    page_icon="⚕️",
    layout="wide"
)


# =====================================================
# CSS
# =====================================================

def cargar_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        pass


cargar_css()


# =====================================================
# BASE DE DATOS
# =====================================================

crear_tablas()


# =====================================================
# FUNCIONES IMC
# =====================================================

def calcular_imc(peso, talla_cm):
    talla_m = talla_cm / 100
    return round(peso / (talla_m ** 2), 2)


def diagnostico_imc(imc):
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidad I"
    elif imc < 40:
        return "Obesidad II"
    return "Obesidad III"


# =====================================================
# SESSION STATE
# =====================================================

if "login" not in st.session_state:
    st.session_state.login = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""


# =====================================================
# LOGIN
# =====================================================

def pantalla_login():
    col1, col2, col3 = st.columns([1.2, 1, 1.2])

    with col2:
        st.markdown("""
        <div class="login-card">
            <h1>⚕️ IMC <span>PRO</span></h1>
            <p>Sistema profesional para evaluación del Índice de Masa Corporal.</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])

        with tab1:
            usuario = st.text_input("Usuario", key="login_usuario")
            password = st.text_input(
                "Contraseña",
                type="password",
                key="login_password"
            )

            if st.button("Ingresar"):
                if login_usuario(usuario, password):
                    st.session_state.login = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        with tab2:
            nuevo_usuario = st.text_input("Nuevo usuario", key="nuevo_usuario")
            nueva_password = st.text_input(
                "Nueva contraseña",
                type="password",
                key="nueva_password"
            )

            if st.button("Crear cuenta"):
                ok, mensaje = registrar_usuario(
                    nuevo_usuario,
                    nueva_password
                )

                if ok:
                    st.success(mensaje)
                else:
                    st.error(mensaje)


# =====================================================
# APLICACIÓN PRINCIPAL
# =====================================================

def dashboard():
    st.sidebar.title("⚕️ IMC PRO")
    st.sidebar.success(f"Usuario: {st.session_state.usuario}")

    menu = st.sidebar.radio(
        "Menú principal",
        [
            "Registrar IMC",
            "Historial",
            "Estadísticas",
            "Exportar"
        ]
    )

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.login = False
        st.session_state.usuario = ""
        st.rerun()

    if menu == "Registrar IMC":
        st.title("📋 Registro de Evaluación IMC")

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombres y apellidos")
            edad = st.number_input(
                "Edad",
                min_value=1,
                max_value=120,
                value=10
            )
            sexo = st.selectbox(
                "Sexo",
                ["Masculino", "Femenino"]
            )

        with col2:
            peso = st.number_input(
                "Peso kg",
                min_value=1.0,
                max_value=300.0,
                value=60.0
            )
            talla = st.number_input(
                "Talla cm",
                min_value=50.0,
                max_value=250.0,
                value=160.0
            )

        if st.button("Calcular y guardar IMC"):
            if nombre.strip() == "":
                st.warning("Ingrese el nombre completo.")
            else:
                imc = calcular_imc(peso, talla)
                diagnostico = diagnostico_imc(imc)

                guardar_imc(
                    nombre=nombre,
                    edad=edad,
                    sexo=sexo,
                    peso=peso,
                    talla=talla,
                    imc=imc,
                    diagnostico=diagnostico
                )

                st.success("Evaluación IMC guardada correctamente.")

                c1, c2 = st.columns(2)
                c1.metric("IMC", imc)
                c2.metric("Diagnóstico", diagnostico)

    elif menu == "Historial":
        st.title("📚 Historial de Evaluaciones IMC")

        df = obtener_datos()

        if df.empty:
            st.info("Aún no existen registros.")
        else:
            st.dataframe(df, use_container_width=True)

    elif menu == "Estadísticas":
        st.title("📊 Estadísticas IMC")

        df = obtener_datos()

        if df.empty:
            st.warning("No existen datos para graficar.")
        else:
            c1, c2, c3 = st.columns(3)

            c1.metric("Total registros", len(df))
            c2.metric("IMC promedio", round(df["imc"].mean(), 2))
            c3.metric("Edad promedio", round(df["edad"].mean(), 2))

            fig1 = px.histogram(
                df,
                x="imc",
                color="sexo",
                title="Distribución del IMC por sexo"
            )
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(
                df,
                names="diagnostico",
                title="Distribución por diagnóstico nutricional"
            )
            st.plotly_chart(fig2, use_container_width=True)

            fig3 = px.scatter(
                df,
                x="peso",
                y="imc",
                color="sexo",
                size="edad",
                title="Relación entre peso e IMC"
            )
            st.plotly_chart(fig3, use_container_width=True)

    elif menu == "Exportar":
        st.title("📥 Exportar Datos")

        df = obtener_datos()

        if df.empty:
            st.info("No hay datos para exportar.")
        else:
            csv = df.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name="imc_pro_registros.csv",
                mime="text/csv"
            )

            st.dataframe(df, use_container_width=True)


# =====================================================
# MAIN
# =====================================================

if st.session_state.login:
    dashboard()
else:
    pantalla_login()