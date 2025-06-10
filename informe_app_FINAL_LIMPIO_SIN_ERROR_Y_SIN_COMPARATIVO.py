import plotly.express as px

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Facturas enviadas a la EPS y las que estan cargadas en el sistema mas no enviadas a las eps", layout="wide")

ruta_excel = r"C:\Users\USUARIO\iCloudDrive\Documents\2025\Desarrollos\Informes quibdo\radicado en dinamia y radicado EPS\Data\informe_radicados_limpio.xlsx"

@st.cache_data
def cargar_datos():
    df = pd.read_excel(ruta_excel)
    df = df.rename(columns={
        "NOMPLBE": "Nombre Aseguradora",
        "FECHA RAD": "Fecha de Radicación en el sistema Dinámica"
    })
    df['Fecha de Radicación en el sistema Dinámica'] = pd.to_datetime(df['Fecha de Radicación en el sistema Dinámica'], errors='coerce')
    df['AÑO'] = df['Fecha de Radicación en el sistema Dinámica'].dt.year
    df['MES'] = df['Fecha de Radicación en el sistema Dinámica'].dt.month
    df['ESTADO'] = df['ESTADO'].replace({
        "Ya fue radicado en la EPS": "Radicado en el sistema Dinámica",
        "Radicado solo en el sistema, sin enviar a la EPS": "Pendiente por enviar a la aseguradora"
    })
    return df

df = cargar_datos()

st.title("📊 Facturas enviadas a la EPS y las que están cargadas en el sistema mas no enviadas a las EPS")

# === NUEVO BLOQUE: Desglose estratégico de los $14.900 millones por año, mes y aseguradora ===
st.markdown("## 📌 Estrategia Inicial: Desglose de $14.900 millones pendientes por enviar")
pendientes_full = df[df['ESTADO'] == "Pendiente por enviar a la aseguradora"]
estrategico = pendientes_full.groupby(['AÑO', 'MES', 'Nombre Aseguradora'])['TOTAL RADICADO'].sum().reset_index()
total_estrategico = estrategico['TOTAL RADICADO'].sum()
estrategico.loc[len(estrategico)] = ["", "", "TOTAL", total_estrategico]
estrategico['TOTAL RADICADO'] = estrategico['TOTAL RADICADO'].apply(lambda x: f"${x:,.0f}")
st.dataframe(estrategico, use_container_width=True)

# === PANEL RESUMEN INICIAL ===
st.markdown("## 📌 Resumen General por Estado")
total = df['TOTAL RADICADO'].sum()
radicado_dinamica = df[df['ESTADO'] == "Radicado en el sistema Dinámica"]['TOTAL RADICADO'].sum()
pendiente_envio = df[df['ESTADO'] == "Pendiente por enviar a la aseguradora"]['TOTAL RADICADO'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Radicado", f"${total:,.0f}")
col2.metric("📤 Radicado en el sistema Dinámica", f"${radicado_dinamica:,.0f}")
col3.metric("⚠️ Pendiente por enviar a la aseguradora", f"${pendiente_envio:,.0f}")

# === DESGLOSE POR AÑO Y MES - ENVIADO VS PENDIENTE ===
st.markdown("## 📅 Desglose por Año y Mes - Radicado vs. Pendiente")
pivot = df.pivot_table(index=['AÑO', 'MES'], columns='ESTADO', values='TOTAL RADICADO', aggfunc='sum').fillna(0).reset_index()
suma_cols = pivot.iloc[:, 2:].sum()
fila_total = pd.DataFrame([[None, None] + suma_cols.tolist()], columns=pivot.columns)
pivot = pd.concat([pivot, fila_total], ignore_index=True)
for col in pivot.columns[2:]:
    pivot[col] = pivot[col].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else x)
st.dataframe(pivot, use_container_width=True)

# === DESGLOSE POR AÑO, MES Y ASEGURADORA ===
st.markdown("## 📊 Desglose por Año, Mes, Aseguradora y Estado")
resumen = df.groupby(['AÑO', 'MES', 'Nombre Aseguradora', 'ESTADO'])['TOTAL RADICADO'].sum().reset_index()
resumen_total = resumen['TOTAL RADICADO'].sum()
resumen.loc[len(resumen)] = ["", "", "TOTAL", "", resumen_total]
resumen['TOTAL RADICADO'] = resumen['TOTAL RADICADO'].apply(lambda x: f"${x:,.0f}")
st.dataframe(resumen, use_container_width=True)

# === TOTAL Y PROMEDIO ENERO-MAYO 2025 ===
st.markdown("## 📆 Total Radicado Ene-May 2025 y Promedio Mensual")
ene_may = df[(df['AÑO'] == 2025) & (df['MES'] <= 5) & (df['ESTADO'] == "Radicado en el sistema Dinámica")]
total_ene_may = ene_may['TOTAL RADICADO'].sum()
promedio_ene_may = total_ene_may / 5
col4, col5 = st.columns(2)
col4.metric("📤 Total Radicado Ene-May 2025", f"${total_ene_may:,.0f}")
col5.metric("📈 Promedio Mensual Ene-May", f"${promedio_ene_may:,.0f}")

# === DETALLE PENDIENTE POR ASEGURADORA Y FECHA ===
st.markdown("## 📌 Total Pendiente por Enviar")
detalle = pendientes_full[['Nombre Aseguradora', 'Fecha de Radicación en el sistema Dinámica', 'TOTAL RADICADO']].copy()
detalle_total = detalle['TOTAL RADICADO'].sum()
detalle.loc[len(detalle)] = ["TOTAL", None, detalle_total]
detalle['TOTAL RADICADO'] = detalle['TOTAL RADICADO'].apply(lambda x: f"${x:,.0f}")
st.dataframe(detalle, use_container_width=True)

# === PENDIENTES POR ANTIGÜEDAD ===
st.markdown("## ⏳ Pendientes por Antigüedad")
pendientes_full['DIAS'] = (pd.to_datetime(datetime.today()) - pendientes_full['Fecha de Radicación en el sistema Dinámica']).dt.days
def clasificar(d):
    if d > 270:
        return '🟥 Mayor a 9 meses'
    elif d > 180:
        return '🟧 Entre 6 y 9 meses'
    elif d > 90:
        return '🟨 Entre 3 y 6 meses'
    else:
        return '🟩 Menor a 3 meses'
pendientes_full['RANGO'] = pendientes_full['DIAS'].apply(clasificar)
agrupado = pendientes_full.groupby('RANGO')['TOTAL RADICADO'].sum().reset_index()
agrupado['TOTAL RADICADO'] = agrupado['TOTAL RADICADO'].apply(lambda x: f"${x:,.0f}")
st.dataframe(agrupado, use_container_width=True)

# === NUEVO BLOQUE: DESGLOSE ESTRATÉGICO POR AÑO Y ASEGURADORA ===
st.markdown("## 🧩 Desglose Estratégico - Pendiente por Enviar a la Aseguradora")
estrategico_simple = pendientes_full.groupby(['AÑO', 'Nombre Aseguradora'])['TOTAL RADICADO'].sum().reset_index()
total_final = estrategico_simple['TOTAL RADICADO'].sum()
estrategico_simple.loc[len(estrategico_simple)] = ["", "TOTAL", total_final]
estrategico_simple['TOTAL RADICADO'] = estrategico_simple['TOTAL RADICADO'].apply(lambda x: f"${x:,.0f}")
st.dataframe(estrategico_simple, use_container_width=True)


# ==========================
# 📊 Gráficas estratégicas al final del reporte
# ==========================

# 1. Comportamiento total radicado por aseguradora y año
comportamiento_radicado = df[df['ESTADO'] == 'Facturas radicadas efectivamente en la EPS']
resumen_radicado = comportamiento_radicado.groupby(['AÑO', 'Nombre Aseguradora'])['TOTAL RADICADO'].sum().reset_index()

# 2. Comportamiento de lo pendiente por aseguradora y año
pendientes_eps = df[df['ESTADO'] == 'Facturas radicadas en Dinámica Gerencial - Pendientes por radicar en la EPS']
resumen_pendientes = pendientes_eps.groupby(['AÑO', 'Nombre Aseguradora'])['TOTAL RADICADO'].sum().reset_index()
