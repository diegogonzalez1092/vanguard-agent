"""
market_data.py
Conexion a datos reales de mercado usando la libreria yfinance.
Obtiene la variacion porcentual del S&P 500 (ticker ^GSPC) durante
los ultimos N dias, para usarla como senal de mercado del agente.
"""

import yfinance as yf


def obtener_variacion_mensual(ticker: str = "^GSPC", dias: int = 30) -> float:
    """
    Devuelve la variacion porcentual del ticker indicado en los ultimos
    `dias` dias corridos. Por defecto usa el S&P 500 (^GSPC).

    Si falla la conexion (sin internet, ticker invalido, etc.) devuelve 0.0
    y avisa por consola, para que el agente pueda seguir funcionando
    con una senal NEUTRAL.
    """
    try:
        data = yf.download(ticker, period=f"{dias}d", progress=False)

        if data.empty or len(data) < 2:
            print(f"[market_data] No se obtuvieron datos suficientes para {ticker}.")
            return 0.0

        precio_inicial = float(data["Close"].iloc[0])
        precio_final = float(data["Close"].iloc[-1])

        variacion_pct = ((precio_final - precio_inicial) / precio_inicial) * 100
        return round(variacion_pct, 2)

    except Exception as e:
        print(f"[market_data] Error al obtener datos de mercado: {e}")
        print("[market_data] Se usara senal NEUTRAL (0.0%) por defecto.")
        return 0.0


if __name__ == "__main__":
    # Prueba rapida: python market_data.py
    variacion = obtener_variacion_mensual()
    print(f"Variacion del S&P 500 en los ultimos 30 dias: {variacion}%")
