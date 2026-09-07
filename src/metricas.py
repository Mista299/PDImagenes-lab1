"""Metricas de error entre experimental y modelos teoricos.

Calcula RMSE, MAE, Pearson y desfase temporal (lag en segundos del maximo
de correlacion cruzada) para theta, omega y alpha:
  - experimental vs M.A.S.
  - experimental vs simulacion no lineal con friccion

Salida: resultados/metricas.csv
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.signal import correlate

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"


def metricas(y_exp: np.ndarray, y_teo: np.ndarray, t: np.ndarray, dt: float
             ) -> dict[str, float]:
    """Calcula las 4 metricas entre dos series del mismo tamano."""
    rmse = float(np.sqrt(np.mean((y_exp - y_teo) ** 2)))
    mae = float(np.mean(np.abs(y_exp - y_teo)))
    # Pearson (constante frente a escala y desplazamiento)
    e_c = y_exp - y_exp.mean()
    t_c = y_teo - y_teo.mean()
    pearson = float(np.dot(e_c, t_c) / (np.linalg.norm(e_c) * np.linalg.norm(t_c) + 1e-12))
    # Desfase: indice del maximo de correlacion cruzada
    corr = correlate(y_exp, y_teo, mode="same")
    lag_idx = int(np.argmax(corr)) - len(y_teo) // 2
    lag_s = lag_idx * dt
    return {"RMSE": rmse, "MAE": mae, "Pearson": pearson, "lag_s": lag_s}


def main() -> None:
    import pandas as pd

    df_c = pd.read_csv(RES / "cinematica.csv")
    df_m = pd.read_csv(RES / "modelos.csv")

    t = df_c["t_s"].to_numpy()
    dt = float(np.median(np.diff(t)))

    theta_exp = df_c["theta_rad"].to_numpy()
    omega_exp = df_c["omega_rad_s"].to_numpy()
    alpha_exp = df_c["alpha_rad_s2"].to_numpy()

    theta_mas = df_m["theta_teo_rad"].to_numpy()
    omega_mas = df_m["omega_teo_rad_s"].to_numpy()
    alpha_mas = df_m["alpha_teo_rad_s2"].to_numpy()

    theta_sim = df_m["theta_sim_rad"].to_numpy()
    omega_sim = df_m["omega_sim_rad_s"].to_numpy()
    alpha_sim = df_m["alpha_sim_rad_s2"].to_numpy()

    filas = []
    print(f"{'variable':<8} {'modelo':<10} {'RMSE':>12} {'MAE':>12} "
          f"{'Pearson':>10} {'lag_s':>8}")
    for nombre, exp, mas, sim in [
        ("theta", theta_exp, theta_mas, theta_sim),
        ("omega", omega_exp, omega_mas, omega_sim),
        ("alpha", alpha_exp, alpha_mas, alpha_sim),
    ]:
        m_mas = metricas(exp, mas, t, dt)
        m_sim = metricas(exp, sim, t, dt)
        filas.append({"variable": nombre, "modelo": "MAS",
                      **{k: float(v) for k, v in m_mas.items()}})
        filas.append({"variable": nombre, "modelo": "no_lineal_friccion",
                      **{k: float(v) for k, v in m_sim.items()}})
        print(f"{nombre:<8} {'MAS':<10} {m_mas['RMSE']:>12.4f} "
              f"{m_mas['MAE']:>12.4f} {m_mas['Pearson']:>10.4f} "
              f"{m_mas['lag_s']:>8.3f}")
        print(f"{nombre:<8} {'sim':<10} {m_sim['RMSE']:>12.4f} "
              f"{m_sim['MAE']:>12.4f} {m_sim['Pearson']:>10.4f} "
              f"{m_sim['lag_s']:>8.3f}")

    out = RES / "metricas.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["variable", "modelo", "RMSE", "MAE",
                                          "Pearson", "lag_s"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nMetricas guardadas en {out}")


if __name__ == "__main__":
    main()
