
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Facturas enviadas a la EPS y las que estan cargadas en el sistema mas no enviadas a las eps", layout="wide")
st.title("📊 Facturas enviadas a la EPS y las que están cargadas en el sistema mas no enviadas a las EPS")

# -------------------------------
# Paso 1: Cargar datos desde Excel
# -------------------------------

@st.cache_data
def cargar_datos():
    ruta_excel = "informe_radicados_limpio.xlsx"  # archivo debe estar en el mismo repositorio
    df = pd.read_excel(ruta_excel)
    return df

df = cargar_datos()

# Visualización rápida de prueba (puedes quitar esto luego)
st.subheader("Vista previa de datos")
st.dataframe(df.head())
