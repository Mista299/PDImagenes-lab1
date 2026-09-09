"""Graficas comparativas experimental vs. teorica (seccion 3.4 del informe).

Usa los resultados ya generados por el resto del pipeline:
  - resultados/cinematica.csv   -> theta_exp, omega_exp, alpha_exp
  - resultados/modelos.csv      -> theta_teo (M.A.S.), theta_sim (no lineal
                                    con friccion), y sus derivadas
  - resultados/metricas.csv     -> RMSE, MAE, Pearson, lag ya calculados
                                    por src/metricas.py

Genera 4 figuras en figs/:
  1. figs/g1_angulo_vs_tiempo.png
  2. figs/g2_velocidad_vs_tiempo.png
  3. figs/g3_aceleracion_vs_tiempo.png
  4. figs/g4_espacio_fases.png

No recalcula RMSE/MAE/Pearson/lag (eso ya lo hace metricas.py); este modulo
solo los lee de resultados/metricas.csv para anotarlos en las graficas y
para imprimir la tabla resumen usada en la seccion 3.4 del .md.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"
FIGS = ROOT / "figs"

# Estilo consistente para las 4 figuras
COLOR_EXP = "#1f77b4"       # azul - experimental
COLOR_MAS = "#d62728"       # rojo - M.A.S. teorico (sin friccion)
COLOR_SIM = "#2ca02c"       # verde - simulacion no lineal con friccion


def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carga cinematica.csv, modelos.csv y metricas.csv."""
    df_c = pd.read_csv(RES / "cinematica.csv")
    df_m = pd.read_csv(RES / "modelos.csv")
    df_met = pd.read_csv(RES / "metricas.csv")
    return df_c, df_m, df_met


def _anotar_metricas(ax, df_met: pd.DataFrame, variable: str) -> None:
    """Agrega un cuadro de texto con RMSE/MAE/Pearson/lag (modelo MAS)."""
    fila = df_met[(df_met["variable"] == variable) & (df_met["modelo"] == "MAS")]
    if fila.empty:
        return
    r = fila.iloc[0]
    texto = (
        f"MAS vs exp.\n"
        f"RMSE={r['RMSE']:.3f}\n"
        f"MAE={r['MAE']:.3f}\n"
        f"Pearson={r['Pearson']:.3f}\n"
        f"lag={r['lag_s']*1000:.0f} ms"
    )
    ax.text(0.02, 0.02, texto, transform=ax.transAxes, fontsize=8,
             va="bottom", ha="left",
             bbox=dict(boxstyle="round", fc="white", ec="0.6", alpha=0.85))


def graficar_angulo(df_c: pd.DataFrame, df_m: pd.DataFrame,
                     df_met: pd.DataFrame) -> Path:
    """1. Grafica de Angulo vs Tiempo: theta_exp(t) vs theta_teorico(t)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df_c["t_s"], np.degrees(df_c["theta_rad"]), color=COLOR_EXP,
            lw=1.6, label=r"$\theta_{exp}(t)$")
    ax.plot(df_m["t_s"], np.degrees(df_m["theta_teo_rad"]), color=COLOR_MAS,
            lw=1.3, ls="--", label=r"$\theta_{MAS}(t)$ (sin fricción)")
    ax.plot(df_m["t_s"], np.degrees(df_m["theta_sim_rad"]), color=COLOR_SIM,
            lw=1.3, ls="-.", label=r"$\theta_{sim}(t)$ (no lineal + fricción)")
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel(r"Ángulo $\theta$ [°]")
    ax.set_title("1. Ángulo vs. Tiempo — Experimental vs. Teórico")
    ax.axhline(0, color="0.8", lw=0.8)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    _anotar_metricas(ax, df_met, "theta")
    fig.tight_layout()
    out = FIGS / "g1_angulo_vs_tiempo.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def graficar_velocidad(df_c: pd.DataFrame, df_m: pd.DataFrame,
                        df_met: pd.DataFrame) -> Path:
    """2. Grafica de Velocidad vs Tiempo: omega_exp(t) vs omega_teorico(t)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df_c["t_s"], df_c["omega_rad_s"], color=COLOR_EXP,
            lw=1.6, label=r"$\omega_{exp}(t)$")
    ax.plot(df_m["t_s"], df_m["omega_teo_rad_s"], color=COLOR_MAS,
            lw=1.3, ls="--", label=r"$\omega_{MAS}(t)$ (sin fricción)")
    ax.plot(df_m["t_s"], df_m["omega_sim_rad_s"], color=COLOR_SIM,
            lw=1.3, ls="-.", label=r"$\omega_{sim}(t)$ (no lineal + fricción)")
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel(r"Velocidad angular $\omega$ [rad/s]")
    ax.set_title("2. Velocidad Angular vs. Tiempo — Experimental vs. Teórico")
    ax.axhline(0, color="0.8", lw=0.8)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    _anotar_metricas(ax, df_met, "omega")
    fig.tight_layout()
    out = FIGS / "g2_velocidad_vs_tiempo.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def graficar_aceleracion(df_c: pd.DataFrame, df_m: pd.DataFrame,
                          df_met: pd.DataFrame) -> Path:
    """3. Grafica de Aceleracion vs Tiempo: alpha_exp(t) vs alpha_teorico(t)."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df_c["t_s"], df_c["alpha_rad_s2"], color=COLOR_EXP,
            lw=1.4, alpha=0.85, label=r"$\alpha_{exp}(t)$")
    ax.plot(df_m["t_s"], df_m["alpha_teo_rad_s2"], color=COLOR_MAS,
            lw=1.3, ls="--", label=r"$\alpha_{MAS}(t)$ (sin fricción)")
    ax.plot(df_m["t_s"], df_m["alpha_sim_rad_s2"], color=COLOR_SIM,
            lw=1.3, ls="-.", label=r"$\alpha_{sim}(t)$ (no lineal + fricción)")
    ax.set_xlabel("Tiempo $t$ [s]")
    ax.set_ylabel(r"Aceleración angular $\alpha$ [rad/s²]")
    ax.set_title("3. Aceleración Angular vs. Tiempo — Experimental vs. Teórico")
    ax.axhline(0, color="0.8", lw=0.8)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.3)
    _anotar_metricas(ax, df_met, "alpha")
    fig.tight_layout()
    out = FIGS / "g3_aceleracion_vs_tiempo.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def graficar_espacio_fases(df_c: pd.DataFrame, df_m: pd.DataFrame) -> Path:
    """4. Retrato de Espacio de Fases (theta, omega): elipse M.A.S. vs.
    espiral experimental amortiguada."""
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    ax.plot(np.degrees(df_c["theta_rad"]), df_c["omega_rad_s"],
            color=COLOR_EXP, lw=1.2, alpha=0.85,
            label=r"Experimental (espiral por amortiguamiento)")
    ax.plot(np.degrees(df_m["theta_teo_rad"]), df_m["omega_teo_rad_s"],
            color=COLOR_MAS, lw=1.4, ls="--",
            label=r"M.A.S. teórico (elipse, sin fricción)")
    ax.plot(np.degrees(df_m["theta_sim_rad"]), df_m["omega_sim_rad_s"],
            color=COLOR_SIM, lw=1.2, ls="-.",
            label=r"Simulación no lineal con fricción")
    # Punto inicial para orientar la lectura de la espiral
    ax.scatter(np.degrees(df_c["theta_rad"].iloc[0]),
               df_c["omega_rad_s"].iloc[0], color=COLOR_EXP, s=40, zorder=5,
               marker="o", label="Inicio (exp.)")
    ax.set_xlabel(r"Ángulo $\theta$ [°]")
    ax.set_ylabel(r"Velocidad angular $\omega$ [rad/s]")
    ax.set_title("4. Retrato de Espacio de Fases $(\\theta, \\omega)$")
    ax.axhline(0, color="0.8", lw=0.8)
    ax.axvline(0, color="0.8", lw=0.8)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_aspect("auto")
    fig.tight_layout()
    out = FIGS / "g4_espacio_fases.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def resumen_metricas(df_met: pd.DataFrame) -> str:
    """Genera una tabla en formato Markdown con las metricas de metricas.csv."""
    lineas = [
        "| Variable | Modelo | RMSE | MAE | Pearson | Desfase (lag) |",
        "|---|---|---|---|---|---|",
    ]
    nombre_modelo = {"MAS": "M.A.S. (sin fricción)",
                      "no_lineal_friccion": "No lineal (con fricción)"}
    unidades = {"theta": "rad", "omega": "rad/s", "alpha": "rad/s²"}
    for _, r in df_met.iterrows():
        var = r["variable"]
        u = unidades.get(var, "")
        lineas.append(
            f"| ${var}$ [{u}] | {nombre_modelo.get(r['modelo'], r['modelo'])} "
            f"| {r['RMSE']:.4f} | {r['MAE']:.4f} | {r['Pearson']:.4f} "
            f"| {r['lag_s']*1000:.0f} ms |"
        )
    return "\n".join(lineas)


def main() -> None:
    FIGS.mkdir(exist_ok=True)
    df_c, df_m, df_met = cargar_datos()

    print("Generando graficas de la seccion 3.4...")
    p1 = graficar_angulo(df_c, df_m, df_met)
    print(f"  [1/4] {p1.relative_to(ROOT)}")
    p2 = graficar_velocidad(df_c, df_m, df_met)
    print(f"  [2/4] {p2.relative_to(ROOT)}")
    p3 = graficar_aceleracion(df_c, df_m, df_met)
    print(f"  [3/4] {p3.relative_to(ROOT)}")
    p4 = graficar_espacio_fases(df_c, df_m)
    print(f"  [4/4] {p4.relative_to(ROOT)}")

    print("\nTabla de metricas (resultados/metricas.csv):\n")
    print(resumen_metricas(df_met))


if __name__ == "__main__":
    main()
