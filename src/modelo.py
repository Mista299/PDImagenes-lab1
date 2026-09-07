"""Modelo fisico del pendulo.

1. M.A.S. analitico (sin friccion, lineal, valido para theta < 15 grados).
2. Simulacion numerica no lineal CON friccion viscosa (RK45 via solve_ivp)
   ajustando el coeficiente b por minimos cuadrados contra los datos.

EDO con friccion: theta'' + (b/mL^2)*theta' + (g/L)*sin(theta) = 0

Salida: resultados/modelos.csv con t_s, theta_teo, omega_teo, alpha_teo,
        theta_sim, omega_sim, alpha_sim
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"
G = 9.81


def mas_analitico(t: np.ndarray, theta0: float, omega_n: float
                  ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Modelo M.A.S. sin friccion. Devuelve (theta, omega, alpha)."""
    theta = theta0 * np.cos(omega_n * t)
    omega = -theta0 * omega_n * np.sin(omega_n * t)
    alpha = -theta0 * omega_n**2 * np.cos(omega_n * t)
    return theta, omega, alpha


def edo_pendulo(t: float, y: np.ndarray, b: float, m: float, L: float
                ) -> list[float]:
    """EDO del pendulo con friccion. y = [theta, omega]."""
    theta, omega = y
    dtheta = omega
    domega = -(b / (m * L**2)) * omega - (G / L) * np.sin(theta)
    return [dtheta, domega]


def simular(theta0: float, b: float, m: float, L: float,
            t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Integra la EDO no lineal con friccion. Devuelve (theta_sim, omega_sim)."""
    sol = solve_ivp(
        edo_pendulo,
        [t[0], t[-1]],
        [theta0, 0.0],
        t_eval=t,
        args=(b, m, L),
        method="RK45",
        rtol=1e-8, atol=1e-10,
    )
    return sol.y[0], sol.y[1]


def estimar_periodo(theta: np.ndarray, t: np.ndarray) -> float:
    """Estima el periodo experimental por autocorrelacion (mas robusto que
    picos: funciona aunque haya amortiguamiento fuerte)."""
    centered = theta - theta.mean()
    xcorr = np.correlate(centered, centered, mode="full")
    xcorr = xcorr[len(theta) - 1:]
    xcorr /= xcorr[0] + 1e-12
    dt = float(np.median(np.diff(t)))
    # Primer maximo significativo despues del origen
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(xcorr, distance=int(0.5 / dt))
    if len(peaks) < 2:
        return float("nan")
    T = (peaks[1] - peaks[0]) * dt
    return float(T)


def ajustar_b(theta_exp: np.ndarray, theta0: float, m: float, L: float,
              t: np.ndarray) -> tuple[float, float]:
    """Busca el b que minimiza el RMSE entre theta_sim y theta_exp."""
    def rmse(b_log: float) -> float:
        b = float(np.exp(b_log))
        try:
            theta_sim, _ = simular(theta0, b, m, L, t)
        except Exception:
            return 1e6
        diff = theta_exp - theta_sim
        return float(np.sqrt(np.mean(diff**2)))

    # Busqueda 1D en escala logaritmica (b puede variar en varios ordenes)
    res = minimize_scalar(rmse, bounds=(np.log(1e-4), np.log(10.0)),
                          method="bounded")
    return float(np.exp(res.x)), float(res.fun)


def main() -> None:
    import pandas as pd

    cal = json.loads((RES / "calibracion.json").read_text())
    df = pd.read_csv(RES / "cinematica.csv")
    t = df["t_s"].to_numpy()
    theta_exp = df["theta_rad"].to_numpy()

    # Usar la L de la calibracion del usuario (NO inferir de T).
    # Esto es lo que pide el usuario: todo experimental.
    L = cal["L_m_clicks"]
    omega_n = cal["omega_n_rad_s"]
    T_exp = cal["T_exp_s"]
    L_target = cal["L_target_m"]
    diff_pct = cal["diferencia_porcentaje"]
    m = 0.1  # masa asumida [kg]

    print(f"  L (clicks)   = {L:.3f} m")
    print(f"  L (referencia) = {L_target:.3f} m  (T_exp = {T_exp:.3f} s)")
    print(f"  Diferencia    = {diff_pct:.1f}%")
    print(f"  omega_n = {omega_n:.3f} rad/s, T = {T_exp:.3f} s")

    # Alinear t=0 con el primer pico de |theta_exp|.
    idx_peak = int(np.argmax(np.abs(theta_exp)))
    t_peak = float(t[idx_peak])
    theta0 = float(theta_exp[idx_peak])
    t0 = t - t_peak

    print(f"  Primer pico experimental: t = {t_peak:.3f} s, theta0 = {np.degrees(theta0):.2f} deg")

    theta_mas, omega_mas, alpha_mas = mas_analitico(t0, theta0, omega_n)
    print(f"  M.A.S. calculado ({len(t0)} puntos)")

    print("  Ajustando b por minimos cuadrados...")
    b_opt, rmse_opt = ajustar_b(theta_exp, theta0, m, L, t0)
    theta_sim, omega_sim = simular(theta0, b_opt, m, L, t0)
    alpha_sim = np.gradient(omega_sim, t0)
    print(f"  b_opt = {b_opt:.5f} N*m*s/rad, RMSE sim = {rmse_opt:.4f} rad "
          f"({np.degrees(rmse_opt):.2f} deg)")

    out = RES / "modelos.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "t_s", "theta_teo_rad", "omega_teo_rad_s", "alpha_teo_rad_s2",
            "theta_sim_rad", "omega_sim_rad_s", "alpha_sim_rad_s2",
        ])
        for i in range(len(t0)):
            w.writerow([
                f"{t0[i]:.4f}",
                f"{theta_mas[i]:.6f}", f"{omega_mas[i]:.6f}",
                f"{alpha_mas[i]:.6f}",
                f"{theta_sim[i]:.6f}", f"{omega_sim[i]:.6f}",
                f"{alpha_sim[i]:.6f}",
            ])
    print(f"  Guardado en {out}")

    params = {
        "theta0_rad": theta0,
        "theta0_deg": float(np.degrees(theta0)),
        "omega_n_rad_s": omega_n,
        "T_MAS_s": T_exp,
        "m_kg": m,
        "L_m_clicks": L,
        "L_target_m": L_target,
        "diferencia_porcentaje": diff_pct,
        "b_opt_Nms_rad": b_opt,
        "rmse_sim_rad": rmse_opt,
        "t_peak_s": t_peak,
    }
    (RES / "modelo_params.json").write_text(json.dumps(params, indent=2))


if __name__ == "__main__":
    main()
