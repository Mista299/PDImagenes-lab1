"""Pipeline completo: tracking + cinematica + modelo + metricas.

Requiere haber corrido antes:  python src/calibrar.py

Ejecuta en cadena:
  1. tracking.py     -> resultados/tracking.csv
  2. cinematica.py   -> resultados/cinematica.csv
  3. modelo.py       -> resultados/modelos.csv + modelo_params.json
  4. metricas.py     -> resultados/metricas.csv
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

import tracking           # noqa: E402
import cinematica         # noqa: E402
import modelo             # noqa: E402
import metricas           # noqa: E402


def paso_tracking() -> None:
    print("\n[1/4] Tracking de la bola...")
    t, x, y = tracking.seguir()
    print(f"  {len(t)} detecciones en {t[-1] - t[0]:.2f} s")
    out = tracking.guardar_csv(t, x, y)
    print(f"  -> {out.relative_to(ROOT)}")


def paso_cinematica() -> None:
    print("\n[2/4] Cinematica (theta, omega, alpha)...")
    t, x, y, cal = cinematica.cargar()
    t_u, theta, omega, alpha = cinematica.cinematica(t, x, y, cal)
    out = cinematica.guardar_csv(t_u, theta, omega, alpha)
    print(f"  theta en [{theta.min():.3f}, {theta.max():.3f}] rad")
    print(f"  omega en [{omega.min():.3f}, {omega.max():.3f}] rad/s")
    print(f"  alpha en [{alpha.min():.3f}, {alpha.max():.3f}] rad/s^2")
    print(f"  -> {out.relative_to(ROOT)}")


def paso_modelo() -> None:
    print("\n[3/4] Modelos (M.A.S. + no lineal con friccion)...")
    modelo.main()


def paso_metricas() -> None:
    print("\n[4/4] Metricas (RMSE, MAE, Pearson, lag)...")
    metricas.main()


def main() -> None:
    if not (ROOT / "resultados" / "calibracion.json").exists():
        raise SystemExit(
            "Falta resultados/calibracion.json. Corre primero:\n"
            "  python src/calibrar.py"
        )
    paso_tracking()
    paso_cinematica()
    paso_modelo()
    paso_metricas()
    print("\nListo. Todos los CSV estan en resultados/")


if __name__ == "__main__":
    main()
