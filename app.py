import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="IMC PRO",
    page_icon="⚕️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#020617,#0f172a,#1e3a8a);
    color: white;
}
.main-title {
    text-align:center;
    color:#38bdf8;
    font-size:42px;
    font-weight:900;
}
.card {
    background:#0f172a;
    padding:25px;
    border-radius:20px;
    border:1px solid rgba(56,189,248,.3);
}
.stButton button {
    width:100%;
    background:linear-gradient(90deg,#2563eb,#06b6d4);
    color:white;
    border:none;
    border-radius:12px;
    height:48px;
    font-weight:900;
}
[data-testid="stMetric"] {
    background:#111827;
    padding:18px;
    border-radius:16px;
    border:1px solid rgba(56,189,248,.25);
}
</style>
""", unsafe_allow_html=True)

if "registros" not in st.session_state:
    st.session_state.registros = []

def diagnostico_imc(imc):
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidad grado I"
    elif imc < 40:
        return "Obesidad grado II"
    else:
        return "Obesidad grado III"

st.markdown('<div class="main-title">⚕️ IMC PRO</div>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;color:#cbd5e1;'>Sistema profesional para cálculo de Índice de Masa Corporal</h4>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Menú principal",
    ["Calcular IMC", "Historial", "Exportar"]
)

if menu == "Calcular IMC":
    st.header("Registro del paciente / estudiante")

    col1, col2, col3 = st.columns(3)

    with col1:
        nombre = st.text_input("Nombres y apellidos")
        edad = st.number_input("Edad", min_value=1, max_value=120, value=10)

    with col2:
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
        peso = st.number_input("Peso kg", min_value=0.0, max_value=300.0, value=0.0)

    with col3:
        talla = st.number_input("Talla cm", min_value=0.0, max_value=250.0, value=0.0)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if st.button("Calcular IMC"):
        if peso <= 0 or talla <= 0 or nombre.strip() == "":
            st.warning("Complete nombre, peso y talla correctamente.")
        else:
            talla_m = talla / 100
            imc = peso / (talla_m ** 2)
            dx = diagnostico_imc(imc)

            st.success("Cálculo realizado correctamente")

            c1, c2 = st.columns(2)
            c1.metric("IMC", f"{imc:.2f}")
            c2.metric("Diagnóstico", dx)

            st.session_state.registros.append({
                "fecha": fecha,
                "nombre": nombre,
                "edad": edad,
                "sexo": sexo,
                "peso_kg": peso,
                "talla_cm": talla,
                "imc": round(imc, 2),
                "diagnostico": dx
            })

elif menu == "Historial":
    st.header("Historial de registros")

    df = pd.DataFrame(st.session_state.registros)

    if df.empty:
        st.info("Aún no hay registros.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "Exportar":
    st.header("Exportar datos")

    df = pd.DataFrame(st.session_state.registros)

    if df.empty:
        st.info("No hay datos para exportar.")
    else:
        csv = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Descargar CSV",
            data=csv,
            file_name="imc_pro.csv",
            mime="text/csv"
        )

        st.dataframe(df, use_container_width=True)