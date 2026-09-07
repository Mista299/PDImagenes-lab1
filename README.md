# Procesamiento Digital de Imágenes — Tarea 1

Péndulo simple: extracción experimental de θ(t), ω(t), α(t) desde el video
`pendulo.mp4`, y comparación cuantitativa con dos modelos teóricos:
**M.A.S.** (sin fricción, analítico) y **simulación no lineal con fricción**
(numérico RK45).

---

## 1. Cómo ejecutar (3 comandos)

```bash
cd /home/mista/Escritorio/udea/2026-II/procesamiento-digital/trabajo1
source .venv_part2/bin/activate        # entorno con OpenCV, NumPy, SciPy, etc.

python src/calibrar.py                 # 1. Calibración interactiva (~30 s)
python src/main.py                     # 2. Pipeline completo (~1 min)
```

### Paso 1 — `calibrar.py`

Abre una ventana con el primer frame. El script:

1. Detecta la bola roja y ajusta un círculo → encuentra el **pivote** automáticamente.
2. Estima el **período experimental T_exp** por cruces por cero (verificación con autocorrelación).
3. Muestra los **extremos auto-detectados** de la cinta métrica (rectángulos amarillos).
4. Pide **2 clics** sobre la cinta (o cerrar ventana para usar auto).
5. Pide el valor en **cm de cada clic**.
6. Calcula `k [m/px]`, `L [m]`, e imprime la diferencia con `L_target = g·T²/(4π²)` como información.

### Paso 2 — `main.py`

Ejecuta en cadena (sin intervención):

1. `tracking.py` → procesa los 1091 frames, guarda `tracking.csv`.
2. `cinematica.py` → calcula θ, ω, α suavizados, guarda `cinematica.csv`.
3. `modelo.py` → genera M.A.S. + simulación no lineal con fricción, guarda `modelos.csv` + `modelo_params.json`.
4. `metricas.py` → calcula RMSE/MAE/Pearson/lag, guarda `metricas.csv`.

---

## 2. Dónde leer los resultados

### Figura principal (lo más visual)

**`figs/validacion_final.png`** — 4 paneles:
- **Arriba:** θ(t) experimental (azul) vs M.A.S. (rojo) vs simulación (verde)
- **Medio-arriba:** ω(t), mismo código de colores
- **Medio-abajo:** α(t), mismo código de colores
- **Abajo:** retrato de **espacio de fases** (θ vs ω) — muestra la **elipse** teórica del M.A.S. conteniendo a la **espiral** de la simulación con fricción, sobre la que se distribuyen los datos experimentales.

### Tabla de métricas (lo más cuantitativo)

**`resultados/metricas.csv`** — 6 filas con la comparación:

```csv
variable,modelo,RMSE,MAE,Pearson,lag_s
theta,MAS,0.1301,0.117,0.773,0.160
theta,no_lineal_friccion,0.1091,0.093,0.740,0.040
omega,MAS,0.5808,0.521,0.774,0.160
omega,no_lineal_friccion,0.4866,0.417,0.737,0.040
alpha,MAS,2.6376,2.358,0.770,0.160
alpha,no_lineal_friccion,1.9888,1.488,0.730,0.040
```

**Cómo leerla:**
- **RMSE** menor = mejor ajuste. La simulación con fricción gana por ~20%.
- **Pearson** cercano a 1 = buena correlación. Ambos modelos > 0.73 porque comparten la misma frecuencia.
- **lag_s** ≈ 0 = no hay desfase temporal.

### Parámetros del péndulo y modelos

**`resultados/modelo_params.json`**:
- `theta0_rad` / `theta0_deg` — amplitud inicial (medida del primer pico)
- `omega_n_rad_s` — frecuencia natural del M.A.S. (de T_exp)
- `T_MAS_s` — período experimental medido
- `L_m_clicks` — longitud calibrada con regla (0.551 m)
- `L_target_m` — longitud inferida del período (0.491 m)
- `diferencia_porcentaje` — discrepancia entre las dos (12%)
- `b_opt_Nms_rad` — coeficiente de fricción ajustado

**`resultados/calibracion.json`** — todos los parámetros de calibración:
- `pivote_xy_px` — coordenadas del pivote en píxeles
- `L_px` — distancia pivote-masa en píxeles
- `k_m_por_px` — factor de escala metros/píxel
- `T_ceros_s`, `T_auto_s` — período medido por dos métodos
- `n_cruces_por_cero` — número de cruces usados para medir T

### Series temporales (para los entregables finales)

**`resultados/tracking.csv`** — `t_s, x_px, y_px` (1091 filas). Para el video anotado.

**`resultados/cinematica.csv`** — `t_s, theta_rad, omega_rad_s, alpha_rad_s2`. Señales experimentales suavizadas.

**`resultados/modelos.csv`** — `t_s, theta_teo, omega_teo, alpha_teo, theta_sim, omega_sim, alpha_sim`. Series teóricas para las gráficas comparativas.

> Documentación detallada de cada CSV en **`resultados/README.md`**.

---

## 3. Resultados actuales (calibración de tu experimento)

| Variable | M.A.S. RMSE | M.A.S. Pearson | Sim. RMSE | Sim. Pearson |
|---|---|---|---|---|
| θ | 7.46° | 0.773 | **6.25°** | 0.740 |
| ω | 0.58 rad/s | 0.774 | **0.49 rad/s** | 0.737 |
| α | 2.64 rad/s² | 0.770 | **2.20 rad/s²** | 0.730 |

**Interpretación:** la simulación con fricción gana ~20% en RMSE porque captura la
pérdida de amplitud que el M.A.S. (sin fricción) no puede reproducir.

**Parámetros físicos calibrados:**
- `L = 0.551 m` (de la regla)
- `T_exp = 1.406 s` (medido del video)
- `θ₀ = 16.6°` (amplitud inicial)
- `b ≈ 0.0008 N·m·s/rad` (fricción)
- `m = 0.1 kg` (asumida)

**Discrepancia documentada (12%):** la regla está ligeramente más lejos de
la cámara que el péndulo → `L_regla > L_real`. Discutir como fuente de error
en sección 3.4 del PDF.

---

## 4. Estructura

```
trabajo1/
├── pendulo.mp4                          # video de entrada (43.64 s, 25 fps)
├── parte1_taller_PDI.ipynb              # taller Parte 1 (entregado)
├── TAREA_1_PENDULO_SIMPLE.md            # enunciado en markdown
├── PLAN_PARTE2.md                       # plan detallado Parte 2
├── REPORTE_INSPECCION.md                # reporte de Fase 0
├── README.md                            # este archivo
│
├── src/                                 # código fuente modular
│   ├── calibrar.py                      # calibración interactiva + pivote + T
│   ├── tracking.py                      # pipeline HSV → centroide (paso 2-6 del PDF)
│   ├── cinematica.py                    # θ, ω, α con Savitzky-Golay (paso 7)
│   ├── modelo.py                        # M.A.S. analítico + simulación RK45
│   ├── metricas.py                      # RMSE, MAE, Pearson, lag
│   └── main.py                          # corre todo el pipeline
│
├── resultados/                          # datos generados (ver sección 2)
│   ├── README.md
│   ├── calibracion.json
│   ├── tracking.csv
│   ├── cinematica.csv
│   ├── modelos.csv
│   ├── modelo_params.json
│   └── metricas.csv
│
└── figs/                                # figuras
    ├── validacion_final.png             # θ, ω, α vs t + espacio de fases
    └── tracking_validacion.png          # trayectoria detectada sobre frame
```

---

## 5. Reparto de tareas

| Entregable | Responsable | Estado |
|---|---|---|
| Calibración, tracking, cinemática, modelos, métricas, CSVs | Yo | ✅ Listo |
| Gráfica comparativa final (composición estética) | Compañeros | Pendiente |
| Video anotado con telemetría (`pendulo_anotado.mp4`) | Compañeros | Pendiente |
| Artículo IEEE (≤6 págs) | Todos | Pendiente |
| Diapositivas (≤8) | Todos | Pendiente |

---

## 6. Requisitos

- Python 3.12+
- Paquetes: `opencv-python`, `numpy`, `scipy`, `matplotlib`, `pandas`, `tqdm`
- Entorno virtual: `.venv_part2/` ya creado con todo instalado

```bash
# Si necesitas recrear el entorno desde cero:
python -m venv .venv_part2
source .venv_part2/bin/activate
pip install opencv-python numpy scipy matplotlib pandas tqdm
```
