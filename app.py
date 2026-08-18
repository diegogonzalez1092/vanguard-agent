"""
app.py
Interfaz web del agente de inversion, hecha con Streamlit.
Lee el snapshot de datos precalculado (data/market_snapshot.json),
actualizado automaticamente 2 veces por dia por GitHub Actions.
"""

import json
import datetime
from pathlib import Path

import streamlit as st

from portfolio_data import PORTFOLIO, CATEGORY_MAP, RISK_PROFILES
from agent import (
    calcular_pesos_actuales,
    obtener_senal_mercado,
    ajustar_targets_por_senal,
    calcular_brecha,
    asignar_monto,
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
st.info("ℹ️ Esto es información generada con datos públicos, no es asesoramiento financiero. "
        "El rendimiento pasado no garantiza resultados futuros.")

# --- Paso 0: perfil de riesgo ---
st.subheader("1. Tu perfil de riesgo")
perfil = st.radio(
    "¿Qué perfil querés usar para esta recomendación?",
    ["MODERADO", "AGRESIVO"],
    captions=[
        "Más peso en core diversificado, dividendos y renta fija.",
        "Más peso en growth/tech y satélite, menos renta fija.",
    ],
    horizontal=True,
)
target_weights_base = RISK_PROFILES[perfil]

# --- Snapshot de mercado ---
snapshot = cargar_snapshot()
col1, col2 = st.columns([3, 1])
with col1:
    if snapshot:
        fecha = snapshot["actualizado"].replace("T", " ").split(".")[0]
        st.caption(f"🕒 Datos actualizados automáticamente: {fecha} UTC")
    else:
        st.caption("⚠️ Todavía no hay snapshot automático generado.")
with col2:
    refrescar = st.button("🔄 Refrescar ahora")

if refrescar or snapshot is None:
    with st.spinner("Consultando mercado en vivo..."):
        snapshot = calcular_snapshot_en_vivo()

variacion = snapshot["mercado"]["variacion_promedio"]

with st.expander("Ver detalle de fuentes e índices de mercado"):
    st.caption("Fuentes: Yahoo Finance (primaria) y Stooq (respaldo si Yahoo falla).")
    for nombre, datos in snapshot["mercado"]["detalle_indices"].items():
        st.write(f"- **{nombre}**: {datos['valor']}% (fuente: {datos['fuente']})")
    vix = snapshot["mercado"]["vix"]
    st.write(f"- **VIX (volatilidad)**: {vix['valor']} (fuente: {vix['fuente']})")

# --- Paso 2: monto ---
st.subheader("2. Monto a invertir")
opciones_monto = list(range(100, 1001, 100))
monto = st.selectbox("Elegí el monto", opciones_monto, index=opciones_monto.index(500))
monto_custom = st.number_input("...o un monto personalizado (0 = usar el de arriba)", min_value=0.0, value=0.0, step=50.0)
if monto_custom > 0:
    monto = monto_custom

etiquetas = {
    "CORE_GLOBAL": "Core Global",
    "DIVIDENDOS": "Dividendos",
    "GROWTH_TECH": "Growth Tech",
    "BONOS_RENTA_FIJA": "Bonos Renta Fija",
    "SATELITE": "Satélite",
}

# --- Cálculo principal ---
if st.button("Calcular recomendación", type="primary"):
    pesos_actuales = calcular_pesos_actuales(PORTFOLIO, CATEGORY_MAP)
    senal = obtener_senal_mercado(variacion)
    targets_ajustados = ajustar_targets_por_senal(target_weights_base, senal)
    brecha = calcular_brecha(pesos_actuales, targets_ajustados)
    asignacion = asignar_monto(monto, brecha)

    st.subheader("Resultado")
    st.write(f"**Perfil:** {perfil} · **Señal de mercado:** {senal} (variación promedio: {variacion}%)")

    tabla = []
    for cat in target_weights_base:
        tabla.append({
            "Categoría": etiquetas.get(cat, cat),
            "Peso actual": f"{pesos_actuales.get(cat, 0)*100:.2f}%",
            "Target ajustado": f"{targets_ajustados[cat]*100:.2f}%",
            "Monto a invertir": f"${asignacion[cat]:.2f}",
        })
    st.table(tabla)

    st.subheader("💰 Recomendación de compra (mejor opción del mercado)")
    st.caption("No se limita a tu cartera actual: elige la mejor opción disponible por categoría, "
               "priorizando fondos Vanguard cuando son competitivos.")

    for cat, monto_cat in asignacion.items():
        if monto_cat <= 0:
            continue
        nombre_categoria = etiquetas.get(cat, cat)
        mejor = snapshot["oportunidades"].get(cat, {}).get("mejor_opcion")
        if mejor:
            tag = "🟢 Vanguard" if mejor["vanguard"] else "⚪ No Vanguard"
            st.write(
                f"- **{nombre_categoria}** ({tag}): comprar **{mejor['nombre']} ({mejor['ticker']})** "
                f"por **${monto_cat:.2f}** — rendimiento último mes: {mejor['rendimiento_1m_pct']}%"
            )
        else:
            st.write(f"- **{nombre_categoria}**: sin datos de mercado disponibles todavía, "
                      f"revisar manualmente (${monto_cat:.2f}). Probá tocar '🔄 Refrescar ahora' arriba.")

st.divider()

# --- Oportunidades del mercado, vista completa ---
st.subheader("🔎 Oportunidades del mercado por categoría")
for categoria, datos in snapshot["oportunidades"].items():
    st.write(f"**{etiquetas.get(categoria, categoria)}**")
    for item in datos["ranking"]:
        tag = "🟢" if item["vanguard"] else "⚪"
        nombre = item.get("nombre", item["ticker"])
        st.write(f"  {tag} {nombre} ({item['ticker']}): {item['rendimiento_1m_pct']}% (último mes)")

st.divider()
with st.expander("Ver cartera actual cargada"):
    st.json(PORTFOLIO)
