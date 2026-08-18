"""
screener.py
Rankea un universo de ETFs y fondos por rendimiento reciente (momentum de
1 mes), separando cuales son de Vanguard. Cuando un fondo Vanguard tiene
un rendimiento competitivo (dentro de 1 punto porcentual del mejor de su
categoria), se prioriza por sobre alternativas de otras gestoras.

IMPORTANTE: esto es informacion objetiva basada en datos historicos,
NO es una recomendacion de inversion personalizada. El rendimiento pasado
no garantiza rendimiento futuro.
"""

# Cada tupla es (ticker, es_vanguard). Las categorias coinciden con
# CATEGORY_MAP de portfolio_data.py para poder cruzar cartera <-> mercado.
UNIVERSO_CANDIDATOS = {
    "CORE_GLOBAL": [
        ("VTI", True), ("VOO", True), ("VXUS", True), ("VT", True),
        ("SPY", False), ("IVV", False), ("VTSAX", True), ("VFIAX", False),
    ],
    "DIVIDENDOS": [
        ("VYM", True), ("VIG", True), ("VYMI", True),
        ("SCHD", False), ("HDV", False), ("DVY", False),
    ],
    "GROWTH_TECH": [
        ("VUG", True), ("VGT", True), ("VOOG", True),
        ("QQQ", False), ("XLK", False), ("SOXX", False),
    ],
    "BONOS_RENTA_FIJA": [
        ("BND", True), ("BNDX", True), ("VTEB", True),
        ("AGG", False), ("TLT", False),
    ],
    "SATELITE": [
        ("VNQ", True), ("VDE", True), ("VHT", True), ("VFH", True),
        ("XOM", False), ("JPM", False),
    ],
}

TOLERANCIA_VANGUARD_PCT = 1.0  # si un fondo Vanguard esta a <=1pt del mejor, se prioriza


def _rendimiento_1m(ticker: str) -> float | None:
    try:
        import yfinance as yf
        data = yf.download(ticker, period="1mo", progress=False)
        if data.empty or len(data) < 2:
            return None
        inicio = float(data["Close"].iloc[0])
        fin = float(data["Close"].iloc[-1])
        return round(((fin - inicio) / inicio) * 100, 2)
    except Exception:
        return None


def rankear_categoria(candidatos: list[tuple[str, bool]], top_n: int = 5) -> list[dict]:
    resultados = []
    for ticker, es_vanguard in candidatos:
        rendimiento = _rendimiento_1m(ticker)
        if rendimiento is not None:
            resultados.append({
                "ticker": ticker,
                "rendimiento_1m_pct": rendimiento,
                "vanguard": es_vanguard,
            })
    resultados.sort(key=lambda x: x["rendimiento_1m_pct"], reverse=True)
    return resultados[:top_n]


def elegir_mejor_opcion(ranking: list[dict]) -> dict | None:
    """
    De un ranking ya ordenado, elige la mejor opcion priorizando Vanguard
    si esta dentro de la tolerancia respecto al primer puesto.
    """
    if not ranking:
        return None

    mejor_general = ranking[0]
    if mejor_general["vanguard"]:
        return mejor_general

    for item in ranking:
        if item["vanguard"] and (mejor_general["rendimiento_1m_pct"] - item["rendimiento_1m_pct"]) <= TOLERANCIA_VANGUARD_PCT:
            return item

    return mejor_general  # ningun Vanguard competitivo este mes


def generar_oportunidades(top_n: int = 5) -> dict:
    """Devuelve, por categoria: el ranking completo y la mejor opcion elegida."""
    oportunidades = {}
    for categoria, candidatos in UNIVERSO_CANDIDATOS.items():
        ranking = rankear_categoria(candidatos, top_n)
        oportunidades[categoria] = {
            "ranking": ranking,
            "mejor_opcion": elegir_mejor_opcion(ranking),
        }
    return oportunidades


if __name__ == "__main__":
    import json
    print(json.dumps(generar_oportunidades(), indent=2, ensure_ascii=False))
