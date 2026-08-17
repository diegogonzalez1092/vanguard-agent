"""
app.py
Interfaz web (Streamlit) del agente de inversion mensual en Vanguard.

Uso:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st

from portfolio_data import PORTFOLIO, CATEGORY_MAP, TARGET_WEIGHTS
from agent import (
    calcular_pesos_actuales,
    obtener_senal_mercado,
    ajustar_targets_por_senal,
    calcular_brecha,
    asignar_monto,
    recomendar_tickers,
)

st.set_page_config(page_title="Vanguard Auto-Rebalance Agent", page_icon="📈")

st.title("📈 Vanguard Auto-Rebalance Agent")
st.caption(
    "Recomienda en que categorias y tickers invertir tu nuevo aporte mensual, "
    "en base al desbalance de tu cartera y la senal actual del mercado."
)

with st.sidebar:
    st.header("Parametros del aporte")
    monto = st.selectbox("Monto a invertir este mes ($)", [300, 500, 1000], index=1)
    monto_custom = st.number_input("O ingresa un monto personalizado", min_value=0.0, value=0.0, step=50.0)
    if monto_custom > 0:
        monto = monto_custom

    st.header("Senal de mercado")
    modo = st.radio(
        "Origen de la variacion del mercado",
        ["Automatico (Yahoo Finance)", "Manual"],
    )

    variacion = None
    if modo == "Manual":
        variacion = st.number_input(
            "Variacion % del S&P 500 este mes (ej: -6.5)", value=0.0, step=0.1
        )

    ejecutar = st.button("Calcular recomendacion", type="primary")

if ejecutar:
    if modo == "Automatico (Yahoo Finance)":
        try:
            from market_data import obtener_variacion_mensual

            with st.spinner("Consultando variacion real del S&P 500..."):
                variacion = obtener_variacion_mensual()
            st.info(f"Variacion real del S&P 500 (ultimos 30 dias): {variacion}%")
        except ImportError:
            st.warning("No se encontro 'yfinance' instalado. Ingresa la variacion manualmente en el panel lateral.")
            st.stop()

    pesos_actuales = calcular_pesos_actuales(PORTFOLIO, CATEGORY_MAP)
    senal = obtener_senal_mercado(variacion)
    targets_ajustados = ajustar_targets_por_senal(TARGET_WEIGHTS, senal)
    brecha = calcular_brecha(pesos_actuales, targets_ajustados)
    asignacion = asignar_monto(monto, brecha)
    recomendaciones = recomendar_tickers(asignacion, CATEGORY_MAP, PORTFOLIO)

    senal_emoji = {"BAJISTA": "🟢", "ALCISTA": "🔴", "NEUTRAL": "🟡"}
    st.subheader(f"{senal_emoji.get(senal, '')} Senal de mercado ({variacion}%): {senal}")

    st.subheader("Distribucion por categoria")
    tabla = pd.DataFrame(
        {
            "Categoria": list(CATEGORY_MAP.keys()),
            "Peso actual": [f"{pesos_actuales[c] * 100:.2f}%" for c in CATEGORY_MAP],
            "Target ajustado": [f"{targets_ajustados[c] * 100:.2f}%" for c in CATEGORY_MAP],
            "Monto a invertir": [f"${asignacion[c]:.2f}" for c in CATEGORY_MAP],
        }
    )
    st.dataframe(tabla, hide_index=True, use_container_width=True)

    st.subheader("Recomendacion de compra")
    if recomendaciones:
        for cat, data in recomendaciones.items():
            st.markdown(f"- Comprar **{data['ticker']}** por **${data['monto']}** ({cat})")
    else:
        st.write("No hay recomendaciones para este aporte.")
else:
    st.write("Configura los parametros en el panel lateral y presiona **Calcular recomendacion**.")
