"""
portfolio_data.py
Datos de la cartera actual del usuario y su clasificacion por categoria.
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

# Clasificacion de cada ticker por categoria de inversion
CATEGORY_MAP = {
    "CORE_GLOBAL": ["VTSAX", "VXUS", "VEA", "VLXVX"],
    "DIVIDENDOS": ["VYM", "VYMI", "SCHD"],
    "GROWTH_TECH": ["QQQ", "MRVL", "NVDA", "CIBR", "VCR"],
    "SATELITE": ["AMZN", "DELL", "UNH", "HRTX", "VSTM"],
}

# Pesos objetivo (estrategia definida por el usuario) - deben sumar 1.0
TARGET_WEIGHTS = {
    "CORE_GLOBAL": 0.50,
    "DIVIDENDOS": 0.20,
    "GROWTH_TECH": 0.20,
    "SATELITE": 0.10,
}
