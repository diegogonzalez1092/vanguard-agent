"""
agent.py
Logica principal del agente de inversion mensual en Vanguard.
"""


def calcular_pesos_actuales(portfolio: dict, category_map: dict) -> dict:
    """Calcula el % que representa cada categoria sobre el total de la cartera."""
    total = sum(portfolio.values())
    pesos = {}
    for categoria, tickers in category_map.items():
        valor_categoria = sum(portfolio.get(t, 0) for t in tickers)
        pesos[categoria] = valor_categoria / total
    return pesos


def obtener_senal_mercado(variacion_pct: float) -> str:
    """
    Traduce la variacion mensual del mercado (ej: S&P500) en una senal.
    variacion_pct: variacion del mes en porcentaje (ej: -6.5 significa -6.5%)
    """
    if variacion_pct <= -5:
        return "BAJISTA"       # mercado cayo fuerte -> oportunidad de compra
    elif variacion_pct >= 5:
        return "ALCISTA"       # mercado subio fuerte -> mas cautela
    else:
        return "NEUTRAL"


def ajustar_targets_por_senal(target_weights: dict, senal: str) -> dict:
    """
    Ajusta los pesos objetivo segun la senal de mercado.
    En mercado BAJISTA: se prioriza Growth/Tech y Core (comprar en baja).
    En mercado ALCISTA: se prioriza Dividendos y Core (mas defensivo).
    """
    ajustado = target_weights.copy()

    if senal == "BAJISTA":
        ajustado["GROWTH_TECH"] += 0.10
        ajustado["DIVIDENDOS"] -= 0.05
        ajustado["SATELITE"] -= 0.05
    elif senal == "ALCISTA":
        ajustado["DIVIDENDOS"] += 0.10
        ajustado["GROWTH_TECH"] -= 0.05
        ajustado["SATELITE"] -= 0.05

    # Evitar pesos negativos
    for k in ajustado:
        ajustado[k] = max(ajustado[k], 0)

    return ajustado


def calcular_brecha(pesos_actuales: dict, pesos_objetivo: dict) -> dict:
    """Calcula cuanto esta 'atrasada' (underweight) cada categoria."""
    return {
        cat: pesos_objetivo[cat] - pesos_actuales.get(cat, 0)
        for cat in pesos_objetivo
    }


def asignar_monto(monto: float, brecha: dict) -> dict:
    """
    Reparte el nuevo aporte priorizando las categorias mas atrasadas.
    Si ninguna esta atrasada (brecha negativa en todas), reparte segun el target.
    """
    brechas_positivas = {k: v for k, v in brecha.items() if v > 0}

    if not brechas_positivas:
        total = sum(brecha.values()) or 1
        return {k: monto * (v / total) for k, v in brecha.items()}

    total_brecha = sum(brechas_positivas.values())
    asignacion = {}
    for cat in brecha:
        if cat in brechas_positivas:
            asignacion[cat] = monto * (brechas_positivas[cat] / total_brecha)
        else:
            asignacion[cat] = 0.0
    return asignacion


def recomendar_tickers(asignacion_categoria: dict, category_map: dict, portfolio: dict) -> dict:
    """
    Dentro de cada categoria, recomienda el ticker con menor peso actual
    (para reforzar diversificacion interna).
    """
    recomendaciones = {}
    for categoria, monto in asignacion_categoria.items():
        if monto <= 0:
            continue
        tickers = category_map[categoria]
        if not tickers:
            continue
        ticker_sugerido = min(tickers, key=lambda t: portfolio.get(t, 0))
        recomendaciones[categoria] = {
            "ticker": ticker_sugerido,
            "monto": round(monto, 2)
        }
    return recomendaciones
