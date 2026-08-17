"""
screener.py
Rankea un universo curado de ETFs, fondos indice y acciones diversificadas
por rendimiento reciente (momentum de 1 mes), para identificar cuales
vienen mostrando mejor desempeno relativo dentro de cada categoria.

IMPORTANTE: esto es informacion objetiva basada en datos historicos,
NO es una recomendacion de inversion personalizada. El rendimiento pasado
no garantiza rendimiento futuro. Usar como punto de partida para
investigar, no como decision automatica de compra.
"""

UNIVERSO_CANDIDATOS = {
    "ETF_AMPLIO_MERCADO": ["VOO", "SPY", "VTI", "IVV"],
    "ETF_DIVIDENDOS": ["VYM", "SCHD", "DVY", "HDV"],
    "ETF_TECH_GROWTH": ["QQQ", "XLK", "VGT", "SOXX"],
    "FONDOS_INDICE": ["VTSAX", "VFIAX", "FXAIX", "SWPPX"],
    "ACCIONES_DIVERSIFICADAS": ["AAPL", "MSFT", "GOOGL", "JNJ", "PG", "JPM", "XOM"],
}


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


def rankear_categoria(tickers: list[str], top_n: int = 3) -> list[dict]:
    resultados = []
    for t in tickers:
        rendimiento = _rendimiento_1m(t)
        if rendimiento is not None:
            resultados.append({"ticker": t, "rendimiento_1m_pct": rendimiento})
    resultados.sort(key=lambda x: x["rendimiento_1m_pct"], reverse=True)
    return resultados[:top_n]


def generar_oportunidades(top_n: int = 3) -> dict:
    """Devuelve el top N de cada categoria del universo de candidatos."""
    oportunidades = {}
    for categoria, tickers in UNIVERSO_CANDIDATOS.items():
        oportunidades[categoria] = rankear_categoria(tickers, top_n)
    return oportunidades


if __name__ == "__main__":
    import json
    print(json.dumps(generar_oportunidades(), indent=2, ensure_ascii=False))
