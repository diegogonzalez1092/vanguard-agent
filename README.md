# Vanguard Auto-Rebalance Agent

Agente de IA que recomienda mensualmente en que categorias y tickers de mi
cartera de Vanguard invertir un nuevo aporte ($300, $500 o $1000), en base a:

1. El desbalance actual de mi cartera respecto a mis pesos objetivo.
2. La senal real del mercado ese mes (alcista / neutral / bajista), obtenida
   automaticamente desde Yahoo Finance (S&P 500).

## Como funciona

1. Se cargan los holdings actuales (`portfolio_data.py`).
2. Se calcula el % que representa cada categoria (Core Global, Dividendos,
   Growth/Tech, Satelite) sobre el total.
3. Se obtiene la variacion real del S&P 500 del ultimo mes (`market_data.py`).
4. Se ajustan los pesos objetivo segun esa senal de mercado.
5. Se calcula la "brecha" entre el peso actual y el objetivo ajustado.
6. El nuevo aporte se reparte priorizando las categorias mas atrasadas.
7. Dentro de cada categoria, se sugiere el ticker con menor peso actual.

## Estructura del proyecto

```
vanguard-agent/
├── README.md
├── requirements.txt
├── portfolio_data.py   # cartera actual + categorias + pesos objetivo
├── market_data.py       # conexion a la API de mercado (yfinance)
├── agent.py              # logica de rebalanceo del agente
└── main.py                # punto de entrada (CLI)
```

## Instalacion

```bash
git clone https://github.com/<tu-usuario>/vanguard-agent.git
cd vanguard-agent
pip install -r requirements.txt
```

## Uso

Con datos reales de mercado (recomendado, requiere internet):
```bash
python main.py
```

Con variacion de mercado ingresada a mano (sin internet):
```bash
python main.py --manual
```

## Ejemplo de salida

```
Monto a invertir este mes ($300 / $500 / $1000): 500

Variacion real del S&P 500 (ultimos 30 dias): -6.2%

==================================================
  AGENTE DE INVERSION VANGUARD - Aporte: $500.0
==================================================

Senal de mercado (-6.2%): BAJISTA

Categoria      Peso actual    Target ajustado   Monto a invertir
-----------------------------------------------------------------
CORE_GLOBAL     52.34%        50.00%           $0.00
DIVIDENDOS      12.53%        15.00%           $87.32
GROWTH_TECH     23.14%        30.00%           $362.45
SATELITE        11.99%        5.00%            $0.00

Recomendacion de compra:
  -> Comprar VYMI por $87.32 (DIVIDENDOS)
  -> Comprar NVDA por $362.45 (GROWTH_TECH)
```

## Progreso del trabajo practico

- [x] Definicion de la cartera actual y categorias.
- [x] Logica de calculo de pesos y brecha respecto al objetivo.
- [x] Reparto del nuevo aporte segun categorias atrasadas.
- [x] Conexion a API real de mercado (Yahoo Finance via yfinance).
- [x] Senal de mercado dinamica (alcista/neutral/bajista) ajusta los targets.
- [x] Interfaz web (Streamlit), desplegada en Streamlit Community Cloud.
- [x] Multiples fuentes de datos de mercado con fallback (Yahoo Finance + Stooq).
- [x] Senal compuesta por varios indices (S&P 500, Nasdaq, Dow Jones) + VIX.
- [x] Screener de oportunidades (ETFs, fondos indice, acciones) fuera de la cartera.
- [x] Actualizacion automatica 2 veces por dia via GitHub Actions.
- [ ] Historial de aportes y evolucion del rebalanceo.

## Arquitectura de datos automatizados

```
GitHub Actions (cron, 2x/dia)
        │
        ▼
  update_data.py  ──►  market_data.py (Yahoo Finance / Stooq)
        │           ──►  screener.py (ranking de oportunidades)
        ▼
data/market_snapshot.json  (se commitea solo al repo)
        │
        ▼
    app.py (Streamlit)  ──►  lee el snapshot, ya no consulta la API en cada visita
```

## Modulos nuevos

- `market_data.py`: variacion de indices con **fallback entre fuentes** (Yahoo Finance → Stooq).
- `screener.py`: rankea un universo curado de ETFs, fondos indice y acciones por rendimiento
  reciente (1 mes), como punto de partida informativo — no es recomendacion personalizada.
- `update_data.py`: genera `data/market_snapshot.json` con todo lo anterior.
- `.github/workflows/update-data.yml`: corre `update_data.py` automaticamente 2 veces por dia
  (horario de mercado) y commitea el snapshot actualizado.

## Aviso importante

Esta herramienta usa datos publicos y logica de rebalanceo simple con fines educativos.
**No es asesoramiento financiero.** El rendimiento pasado no garantiza resultados futuros.

## Tecnologias

- Python 3.10+
- [yfinance](https://pypi.org/project/yfinance/) y [pandas-datareader](https://pypi.org/project/pandas-datareader/) (Stooq) para datos de mercado
- [Streamlit](https://streamlit.io/) para la interfaz web
- GitHub Actions para automatizacion programada
