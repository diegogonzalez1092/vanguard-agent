"""
portfolio_data.py
Datos de la cartera actual del usuario, clasificacion por categoria,
y perfiles de riesgo (pesos objetivo segun perfil moderado o agresivo).
"""

# Valor actual de cada posicion (en USD)
PORTFOLIO = {
    "VTSAX": 5210.50,
    "VLXVX": 1835.83,
    "VXUS": 1322.71,
    "QQQ": 2198.19,
    "VCR": 1364.02,
    "MRVL": 951.20,
    "VYM": 943.07,
    "CIBR": 489.85,
    "VEA": 517.76,
    "AMZN": 521.55,
    "DELL": 478.86,
    "SCHD": 411.66,
    "UNH": 393.17,
    "VYMI": 442.91,
    "NVDA": 227.18,
    "VSTM": 172.75,
    "HRTX": 67.92,
}

# Clasificacion de cada ticker de la cartera por categoria de inversion.
# Las categorias coinciden con las usadas en screener.py para poder
# cruzar "cuanto tengo hoy" con "cual es la mejor opcion del mercado".
CATEGORY_MAP = {
    "CORE_GLOBAL": ["VTSAX", "VXUS", "VEA", "VLXVX"],
    "DIVIDENDOS": ["VYM", "VYMI", "SCHD"],
    "GROWTH_TECH": ["QQQ", "MRVL", "NVDA", "CIBR", "VCR"],
    "BONOS_RENTA_FIJA": [],  # todavia no tenes bonos en cartera
    "SATELITE": ["AMZN", "DELL", "UNH", "HRTX", "VSTM"],
}

# Pesos objetivo segun perfil de riesgo. Deben sumar 1.0 cada uno.
RISK_PROFILES = {
    "MODERADO": {
        "CORE_GLOBAL": 0.45,
        "DIVIDENDOS": 0.25,
        "GROWTH_TECH": 0.15,
        "BONOS_RENTA_FIJA": 0.10,
        "SATELITE": 0.05,
    },
    "AGRESIVO": {
        "CORE_GLOBAL": 0.35,
        "DIVIDENDOS": 0.10,
        "GROWTH_TECH": 0.40,
        "BONOS_RENTA_FIJA": 0.00,
        "SATELITE": 0.15,
    },
}
