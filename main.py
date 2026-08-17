"""
main.py
Punto de entrada del agente. Ejecutar mensualmente.

Uso:
    python main.py            -> pide monto y usa datos reales de mercado (API)
    python main.py --manual   -> pide monto y variacion de mercado a mano
"""

import sys

from portfolio_data import PORTFOLIO, CATEGORY_MAP, TARGET_WEIGHTS
from agent import (
    calcular_pesos_actuales,
    obtener_senal_mercado,
    ajustar_targets_por_senal,
    calcular_brecha,
    asignar_monto,
    recomendar_tickers,
)


def ejecutar_agente(monto: float, variacion_mercado_pct: float):
    print(f"\n{'='*50}")
    print(f"  AGENTE DE INVERSION VANGUARD - Aporte: ${monto}")
    print(f"{'='*50}\n")

    pesos_actuales = calcular_pesos_actuales(PORTFOLIO, CATEGORY_MAP)
    senal = obtener_senal_mercado(variacion_mercado_pct)
    targets_ajustados = ajustar_targets_por_senal(TARGET_WEIGHTS, senal)
    brecha = calcular_brecha(pesos_actuales, targets_ajustados)
    asignacion = asignar_monto(monto, brecha)
    recomendaciones = recomendar_tickers(asignacion, CATEGORY_MAP, PORTFOLIO)

    print(f"Senal de mercado ({variacion_mercado_pct}%): {senal}\n")
    print(f"{'Categoria':<15}{'Peso actual':<15}{'Target ajustado':<18}{'Monto a invertir'}")
    print("-" * 65)
    for cat in CATEGORY_MAP:
        print(f"{cat:<15}{pesos_actuales[cat]*100:>6.2f}%       "
              f"{targets_ajustados[cat]*100:>6.2f}%           "
              f"${asignacion[cat]:.2f}")

    print("\nRecomendacion de compra:")
    for cat, data in recomendaciones.items():
        print(f"  -> Comprar {data['ticker']} por ${data['monto']} ({cat})")


def main():
    modo_manual = "--manual" in sys.argv

    monto_aporte = float(input("Monto a invertir este mes ($300 / $500 / $1000): "))

    if modo_manual:
        variacion = float(input("Variacion % del mercado este mes (ej: -6.5): "))
    else:
        # Intenta traer la senal compuesta real (S&P 500, Nasdaq, Dow Jones + VIX)
        # via market_data.py. Si falla (sin internet, librerias no instaladas, etc.)
        # cae a modo manual.
        try:
            from market_data import obtener_senal_compuesta
            senal_compuesta = obtener_senal_compuesta()
            variacion = senal_compuesta["variacion_promedio"]

            print(f"\nVariacion promedio de mercado (ultimos 30 dias): {variacion}%")
            for nombre, datos in senal_compuesta["detalle_indices"].items():
                print(f"  - {nombre}: {datos['valor']}% (fuente: {datos['fuente']})")
            vix = senal_compuesta["vix"]
            print(f"  - VIX (volatilidad): {vix['valor']} (fuente: {vix['fuente']})")
        except ImportError:
            print("\n[!] No se encontraron las librerias de datos de mercado instaladas. Usando modo manual.")
            variacion = float(input("Variacion % del mercado este mes (ej: -6.5): "))

    ejecutar_agente(monto_aporte, variacion)


if __name__ == "__main__":
    main()
