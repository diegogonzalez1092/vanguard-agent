"""
app.py
Interfaz web del agente de inversion, hecha con Streamlit.
Lee el snapshot de datos precalculado (data/market_snapshot.json),
actualizado automaticamente 2 veces por dia por GitHub Actions.
Si el snapshot no existe o esta desactualizado, permite refrescar en vivo.
"""

import json
import datetime
from pathlib import Path

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

st.set_page_config(page_title="Vanguard Auto-Rebalance Agent", page_icon="📈", layout="centered")

SNAPSHOT_PATH = Path("data/market_snapshot.json")


def cargar_snapshot():
    if SNAPSHOT_PATH.exists():
        with open(SNAPSHOT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def calcular_snapshot_en_vivo():
    from market_data import obtener_senal_compuesta
    from screener import generar_oportunidades
    return {
        "actualizado": datetime.datetime.utcnow().isoformat() + "Z",
        "mercado": obtener_senal_compuesta(),
        "oportunidades": generar_oportunidades(),
    }


st.title("📈 Vanguard Auto-Rebalance Agent")
st.caption("Recomendación de dónde invertir tu aporte, según tu cartera y el mercado.")
st.info("ℹ️ Esto es información generada con datos públicos, no es asesoramiento financiero. "
        "El rendimiento pasado no garantiza resultados futuros.")

snapshot = cargar_snapshot()

col1, col2 = st.columns([3, 1])
with col1:
    if snapshot:
        fecha = snapshot["actualizado"].replace("T", " ").split(".")[0]
        st.caption(f"🕒 Datos actualizados automáticamente: {fecha} UTC")
    else:
        st.caption("⚠️ Todavía no hay snapshot automático generado (el primer run de GitHub Actions puede tardar).")
with col2:
    refrescar = st.button("🔄 Refrescar ahora")

if refrescar or snapshot is None:
    with st.spinner("Consultando mercado en vivo..."):
        snapshot = calcular_snapshot_en_vivo()

variacion = snapshot["mercado"]["variacion_promedio"]

# --- Detalle de fuentes usadas ---
with st.expander("Ver detalle de fuentes de mercado"):
    for nombre, datos in snapshot["mercado"]["detalle_indices"].items():
        st.write(f"- **{nombre}**: {datos['valor']}% (fuente: {datos['fuente']})")
    vix = snapshot["mercado"]["vix"]
    st.write(f"- **VIX (volatilidad)**: {vix['valor']} (fuente: {vix['fuente']})")

# --- Entradas del usuario ---
st.subheader("1. Monto a invertir")
monto = st.selectbox("Elegí el monto", [300, 500, 1000], index=1)
monto_custom = st.number_input("...o un monto personalizado (0 = usar el de arriba)", min_value=0.0, value=0.0, step=50.0)
if monto_custom > 0:
    monto = monto_custom

if st.button("Calcular recomendación para mi cartera", type="primary"):
    pesos_actuales = calcular_pesos_actuales(PORTFOLIO, CATEGORY_MAP)
    senal = obtener_senal_mercado(variacion)
    targets_ajustados = ajustar_targets_por_senal(TARGET_WEIGHTS, senal)
    brecha = calcular_brecha(pesos_actuales, targets_ajustados)
    asignacion = asignar_monto(monto, brecha)
    recomendaciones = recomendar_tickers(asignacion, CATEGORY_MAP, PORTFOLIO)

    st.subheader("Resultado")
    st.write(f"**Señal de mercado:** {senal} (variación promedio de índices: {variacion}%)")

    tabla = []
    for cat in CATEGORY_MAP:
        tabla.append({
            "Categoría": cat,
            "Peso actual": f"{pesos_actuales[cat]*100:.2f}%",
            "Target ajustado": f"{targets_ajustados[cat]*100:.2f}%",
            "Monto a invertir": f"${asignacion[cat]:.2f}",
        })
    st.table(tabla)

    st.subheader("💰 Recomendación dentro de tu cartera")
    if recomendaciones:
        for cat, data in recomendaciones.items():
            st.write(f"- **Comprar {data['ticker']}** por **${data['monto']}** ({cat})")
    else:
        st.write("No hay recomendaciones de compra este mes (cartera ya balanceada).")

st.divider()

# --- Oportunidades fuera de la cartera actual ---
st.subheader("🔎 Oportunidades del mercado (fuera de tu cartera)")
st.caption("Top ETFs, fondos índice y acciones diversificadas por rendimiento del último mes.")

etiquetas = {
    "ETF_AMPLIO_MERCADO": "ETFs de mercado amplio",
    "ETF_DIVIDENDOS": "ETFs de dividendos",
    "ETF_TECH_GROWTH": "ETFs de tecnología / growth",
    "FONDOS_INDICE": "Fondos índice",
    "ACCIONES_DIVERSIFICADAS": "Acciones diversificadas",
}

for categoria, top in snapshot["oportunidades"].items():
    st.write(f"**{etiquetas.get(categoria, categoria)}**")
    if top:
        for item in top:
            st.write(f"  - {item['ticker']}: {item['rendimiento_1m_pct']}% (último mes)")
    else:
        st.write("  - Sin datos disponibles.")

st.divider()
with st.expander("Ver cartera actual cargada"):
    st.json(PORTFOLIO)
