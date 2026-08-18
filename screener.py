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

# Nombre completo de cada fondo/ETF/empresa, para mostrar junto al ticker.
NOMBRES = {
    "VTI": "Vanguard Total Stock Market ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "VXUS": "Vanguard Total International Stock ETF",
    "VT": "Vanguard Total World Stock ETF",
    "SPY": "SPDR S&P 500 ETF Trust",
    "IVV": "iShares Core S&P 500 ETF",
    "VTSAX": "Vanguard Total Stock Market Index Fund",
    "VFIAX": "Vanguard 500 Index Fund (Admiral)",
    "VYM": "Vanguard High Dividend Yield ETF",
    "VIG": "Vanguard Dividend Appreciation ETF",
    "VYMI": "Vanguard International High Dividend Yield ETF",
    "SCHD": "Schwab U.S. Dividend Equity ETF",
    "HDV": "iShares Core High Dividend ETF",
    "DVY": "iShares Select Dividend ETF",
    "VUG": "Vanguard Growth ETF",
    "VGT": "Vanguard Information Technology ETF",
    "VOOG": "Vanguard S&P 500 Growth ETF",
    "QQQ": "Invesco QQQ Trust (Nasdaq-100)",
    "XLK": "Technology Select Sector SPDR Fund",
    "SOXX": "iShares Semiconductor ETF",
    "BND": "Vanguard Total Bond Market ETF",
    "BNDX": "Vanguard Total International Bond ETF",
    "VTEB": "Vanguard Tax-Exempt Bond ETF",
    "AGG": "iShares Core U.S. Aggregate Bond ETF",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "VNQ": "Vanguard Real Estate ETF",
    "VDE": "Vanguard Energy ETF",
    "VHT": "Vanguard Health Care ETF",
    "VFH": "Vanguard Financials ETF",
    "XOM": "Exxon Mobil Corp",
    "JPM": "JPMorgan Chase & Co",
}

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


def _rendimiento_1m(ticker: str) -> dict:
    """
    Obtiene el rendimiento de 1 mes usando el mismo mecanismo multi-fuente
    (Yahoo Finance -> Stooq) que market_data.py, para no depender solo de
    Yahoo (que a veces bloquea consultas desde servidores en la nube).
    """
    from market_data import obtener_variacion
    return obtener_variacion(ticker, dias=30)


def rankear_categoria(candidatos: list[tuple[str, bool]], top_n: int = 5) -> list[dict]:
    resultados = []
    for ticker, es_vanguard in candidatos:
        resultado = _rendimiento_1m(ticker)
        if resultado["valor"] is not None:
            resultados.append({
                "ticker": ticker,
                "nombre": NOMBRES.get(ticker, ticker),
                "rendimiento_1m_pct": resultado["valor"],
                "fuente": resultado["fuente"],
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
