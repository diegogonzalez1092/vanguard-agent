"""
market_data.py
Obtiene senales de mercado desde multiples fuentes, con fallback automatico
si alguna falla:

  1) Yahoo Finance (via yfinance) - fuente primaria
  2) Stooq (via pandas_datareader) - fuente secundaria de respaldo

Nota: Vanguard no ofrece una API publica gratuita de datos de mercado.
Como aproximacion robusta, se combinan varios indices (S&P 500, Nasdaq,
Dow Jones) y el VIX (indice de volatilidad) para armar una senal compuesta,
en vez de depender de un unico ticker o fuente.
"""

import statistics

INDICES = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",     # empresas chicas/medianas - amplia la lectura mas alla de las grandes tech
    "MSCI World (proxy VT)": "VT",  # mercado global, no solo EE.UU.
}
VOLATILIDAD = "^VIX"


def _variacion_yfinance(ticker: str, dias: int = 30) -> float:
    import yfinance as yf
    data = yf.download(ticker, period=f"{dias}d", progress=False)
    if data.empty or len(data) < 2:
        raise ValueError(f"Sin datos suficientes para {ticker} (yfinance)")
    inicio = float(data["Close"].iloc[0])
    fin = float(data["Close"].iloc[-1])
    return round(((fin - inicio) / inicio) * 100, 2)


def _variacion_stooq(ticker_yahoo: str, dias: int = 30) -> float:
    """Fuente secundaria de respaldo. Stooq usa simbolos distintos a Yahoo."""
    import pandas_datareader.data as web
    import datetime

    mapa_stooq = {
        "^GSPC": "^SPX", "^IXIC": "^NDQ", "^DJI": "^DJI", "^VIX": "^VIX",
        "^RUT": "^RUT", "VT": "VT.US",
    }
    simbolo = mapa_stooq.get(ticker_yahoo, ticker_yahoo)

    fin = datetime.date.today()
    inicio = fin - datetime.timedelta(days=dias + 5)
    data = web.DataReader(simbolo, "stooq", inicio, fin)
    data = data.sort_index()
    if data.empty or len(data) < 2:
        raise ValueError(f"Sin datos suficientes para {simbolo} (stooq)")
    precio_inicio = float(data["Close"].iloc[0])
    precio_fin = float(data["Close"].iloc[-1])
    return round(((precio_fin - precio_inicio) / precio_inicio) * 100, 2)


def obtener_variacion(ticker: str, dias: int = 30) -> dict:
    """
    Intenta obtener la variacion de un ticker probando varias fuentes.
    Devuelve {"valor": float, "fuente": str} o {"valor": None, "fuente": "N/A"}
    si todas las fuentes fallan.
    """
    for nombre_fuente, funcion in [
        ("Yahoo Finance", _variacion_yfinance),
        ("Stooq", _variacion_stooq),
    ]:
        try:
            valor = funcion(ticker, dias)
            return {"valor": valor, "fuente": nombre_fuente}
        except Exception:
            continue
    return {"valor": None, "fuente": "N/A"}


def obtener_senal_compuesta(dias: int = 30) -> dict:
    """
    Combina la variacion de varios indices en una sola senal de mercado,
    mas robusta que depender de un unico indice o fuente.
    """
    resultados = {}
    for nombre, ticker in INDICES.items():
        resultados[nombre] = obtener_variacion(ticker, dias)

    valores_validos = [r["valor"] for r in resultados.values() if r["valor"] is not None]
    variacion_promedio = round(statistics.mean(valores_validos), 2) if valores_validos else 0.0

    vix = obtener_variacion(VOLATILIDAD, dias)

    return {
        "variacion_promedio": variacion_promedio,
        "detalle_indices": resultados,
        "vix": vix,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(obtener_senal_compuesta(), indent=2, ensure_ascii=False))
