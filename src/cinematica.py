"""Cinematica experimental del pendulo (paso 7 del PDF).

Calcula theta(t), omega(t) y alpha(t) a partir del tracking, suavizando
con Savitzky-Golay antes de derivar para no amplificar ruido.

Salida: resultados/cinematica.csv con t_s, theta_rad, omega_rad_s, alpha_rad_s2
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"

WINDOW = 31        # ventana de Savitzky-Golay (impar, >= 5)
POLY = 3           # orden del polinomio local


def cargar() -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Lee tracking.csv y calibracion.json. Devuelve (t, x, y, cal)."""
    import pandas as pd
    df = pd.read_csv(RES / "tracking.csv")
    cal = json.loads((RES / "calibracion.json").read_text())
    return df["t_s"].to_numpy(), df["x_px"].to_numpy(), df["y_px"].to_numpy(), cal


def cinematica(t: np.ndarray, x: np.ndarray, y: np.ndarray,
               cal: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Devuelve (t, theta_suave, omega, alpha) sobre una grilla uniforme.

    theta_suave ya esta en radianes. omega y alpha en rad/s y rad/s^2.
    """
    x0, y0 = cal["pivote_xy_px"]
    # Interpolar a grilla uniforme de 25 Hz para derivadas consistentes
    t_uniform = np.arange(t[0], t[-1], 1.0 / 25.0)
    x_u = np.interp(t_uniform, t, x)
    y_u = np.interp(t_uniform, t, y)

    theta = np.arctan2(x_u - x0, y_u - y0)

    # Suavizar antes de derivar para no amplificar ruido
    theta_s = savgol_filter(theta, window_length=WINDOW, polyorder=POLY,
                            mode="nearest")

    omega = np.gradient(theta_s, t_uniform)
    alpha = np.gradient(omega, t_uniform)

    return t_uniform, theta_s, omega, alpha


def guardar_csv(t: np.ndarray, theta: np.ndarray, omega: np.ndarray,
                alpha: np.ndarray) -> Path:
    out = RES / "cinematica.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "theta_rad", "omega_rad_s", "alpha_rad_s2"])
        for ti, th, om, al in zip(t, theta, omega, alpha):
            w.writerow([f"{ti:.4f}", f"{th:.6f}", f"{om:.6f}", f"{al:.6f}"])
    return out


def main() -> None:
    t, x, y, cal = cargar()
    print(f"  Cargadas {len(t)} muestras de tracking.")
    t_u, theta, omega, alpha = cinematica(t, x, y, cal)
    print(f"  Grilla uniforme: {len(t_u)} muestras, {t_u[-1] - t_u[0]:.2f} s")
    print(f"  theta en [{theta.min():.4f}, {theta.max():.4f}] rad")
    print(f"  omega en [{omega.min():.4f}, {omega.max():.4f}] rad/s")
    out = guardar_csv(t_u, theta, omega, alpha)
    print(f"  Guardado en {out}")
    print(f"  Amplitud inicial: {np.degrees(np.abs(theta[0])):.2f} deg")


if __name__ == "__main__":
    main()
