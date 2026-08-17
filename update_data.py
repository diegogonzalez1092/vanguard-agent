"""
update_data.py
Actualiza el snapshot de datos de mercado y oportunidades, y lo guarda
en data/market_snapshot.json. Pensado para ser ejecutado automaticamente
por GitHub Actions dos veces por dia (ver .github/workflows/update-data.yml),
para que la app web lea datos ya calculados en vez de consultar la API
cada vez que alguien la abre.
"""

import json
import datetime
from pathlib import Path

from market_data import obtener_senal_compuesta
from screener import generar_oportunidades


def main():
    snapshot = {
        "actualizado": datetime.datetime.utcnow().isoformat() + "Z",
        "mercado": obtener_senal_compuesta(),
        "oportunidades": generar_oportunidades(),
    }

    Path("data").mkdir(exist_ok=True)
    with open("data/market_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print("Snapshot actualizado correctamente en data/market_snapshot.json")


if __name__ == "__main__":
    main()
