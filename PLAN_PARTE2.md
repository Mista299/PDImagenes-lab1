# PLAN DETALLADO — PARTE 2: Proyecto Péndulo Simple (70%)

## 0. Contexto y punto de partida

- **Video:** `pendulo.mp4` → 1080 × 1920 vertical, 25 fps, 43.64 s, 1091 frames, H.264.
- **Parte 1** (taller PDI): ya entregada en `parte1_taller_PDI.ipynb` (30%).
- **Objetivo Parte 2:** pipeline Python+OpenCV que extraiga `θ(t)`, `ω(t)`, `α(t)` desde el video, los contraste con el modelo M.A.S. (sin fricción) y la simulación numérica no lineal (con fricción), y entregue CSVs listos para que los compañeros compongan la gráfica comparativa y el video anotado.

---

## 1. Resumen ejecutivo

| Sección del PDF | Qué pide | Entregable |
|---|---|---|
| 3.1 Modelo físico | EDO con fricción + fórmulas M.A.S. para θ < 15° | Documentado en el código y se usa en `modelo.py` |
| 3.2 Montaje | Plano ortogonal, fondo uniforme, marcadores A (pivote) y B (masa), regla 30 cm | Video original (ya grabado) |
| 3.3 Pipeline PDI | 7 pasos: calibración → HSV → máscara → morfología → centroide → ángulo → derivación suavizada | `src/*.py` |
| 3.4 Comparación | Gráficas θ/ω/α experimentales vs teóricas, retrato de fases, métricas | CSVs en `resultados/` |
| 3.5 Video anotado | Estela, geometría pivote-masa, panel de telemetría | **Compañeros** |
| 4. Entregables | Notebook Parte 1, video original, video anotado, código, informe IEEE ≤6 págs, diapositivas ≤8 | Informe y diapositivas se arman entre todos al final |

---

## 2. Estructura de carpetas (mínima, todo en .py)

```
trabajo1/
├── pendulo.mp4
├── parte1_taller_PDI.ipynb        # ya entregado (Parte 1)
├── PLAN_PARTE2.md                  # este archivo
├── src/
│   ├── calibrar.py                 # clic en regla + auto-pivote
│   ├── tracking.py                 # pipeline pasos 2-6
│   ├── cinematica.py               # paso 7 (Savitzky-Golay)
│   ├── modelo.py                   # M.A.S. + simulación no lineal
│   ├── metricas.py                 # RMSE, MAE, Pearson, desfase
│   └── main.py                     # corre todo el pipeline
└── resultados/
    ├── calibracion.json
    ├── tracking.csv                # t_s, x_px, y_px
    ├── cinematica.csv              # t_s, theta_rad, omega_rad_s, alpha_rad_s2
    ├── modelos.csv                 # t_s, theta_teo, omega_teo, alpha_teo, theta_sim, omega_sim, alpha_sim
    └── metricas.csv                # variable, RMSE, MAE, Pearson, lag_s
```

---

## 3. Pipeline (orden de ejecución)

```
1. python src/calibrar.py    → resultados/calibracion.json
2. python src/main.py         → corre tracking + cinematica + modelo + metricas
   (equivalente a invocar 2-5 en cadena, pero con un solo comando)
```

### Paso 1 — `calibrar.py`
- Tracking rápido (cada 4 frames) de la bola roja.
- Ajuste de círculo a las posiciones → pivote `(x₀, y₀)`.
- Ventana interactiva: usuario hace **clic en 2 marcas conocidas** de la regla.
- Guarda pivote, radio L (px), `k [m/px]`, `L [m]`, `ωₙ`, `T_MAS`.

### Paso 2 — `tracking.py` (dentro de main.py)
- Para **cada frame** (los 1091):
  1. BGR → HSV
  2. GaussianBlur(5×5, σ=1)
  3. `inRange` con doble rango para rojo (H 0-10 ∪ 170-180, S≥100, V≥60)
  4. Opening (kernel elíptico 5×5, 1 iter) → quita ruido sal
  5. Closing (kernel elíptico 5×5, 1 iter) → rellena huecos
  6. `findContours` → contorno de mayor área
  7. Momentos → `(cx, cy)`
- Output: `tracking.csv` con `t_s, x_px, y_px`

### Paso 3 — `cinematica.py` (dentro de main.py)
- `θ(t) = atan2(x − x₀, y − y₀)`
- `t = np.arange(n) / 25`
- `θ_suave = savgol_filter(θ, window_length=31, polyorder=3)`
- `ω = np.gradient(θ_suave, t)`
- `α = np.gradient(ω, t)`
- Output: `cinematica.csv`

### Paso 4 — `modelo.py` (dentro de main.py)
- **M.A.S.** (sin fricción): `θ_MAS = θ₀·cos(ωₙ·t)`, análogo para ω, α.
- **No lineal con fricción**: `solve_ivp` sobre `θ̈ + (b/mL²)·θ̇ + (g/L)·sin(θ) = 0`, parte de `θ(0)=θ₀, θ̇(0)=0`.
- Ajuste de `b` por barrido + minimización de RMSE contra `θ_exp`.
- Output: `modelos.csv`

### Paso 5 — `metricas.py` (dentro de main.py)
- RMSE, MAE, Pearson, desfase temporal (correlación cruzada) para `(θ, ω, α)`:
  - experimental vs M.A.S.
  - experimental vs simulación no lineal
- Output: `metricas.csv`

---

## 4. Decisiones técnicas justificadas

| Decisión | Razón |
|---|---|
| Solo `.py`, sin notebook | Diapositivas e informe se arman entre todos al final |
| Pivote por ajuste de círculo | No hay marcador visible en el video |
| Calibración interactiva de regla | Auto-detección de marcas no es fiable en este video |
| Doble rango HSV (0-10 y 170-180) | El rojo en OpenCV aparece en ambos extremos del círculo H |
| Savitzky-Golay (31, 3) | Video a 25 fps → ventana 31 ≈ 1.24 s, captura ~media oscilación |
| Masa asumida `m = 0.1 kg` | Valor típico de bola decorativa; se ajustará al refinar |
| Sin pivote forzado a `(540, y₀)` | Se calcula por geometría del círculo de barrido |

---

## 5. Reparto de tareas

| # | Entregable | Responsable |
|---|---|---|
| 1 | Calibración (k, pivote) | Yo |
| 2 | Tracking completo | Yo |
| 3 | Cinemática (θ, ω, α suavizados) | Yo |
| 4 | Modelos M.A.S. y no lineal con fricción | Yo |
| 5 | Métricas (RMSE, MAE, Pearson, desfase) | Yo |
| 6 | 4 CSVs en `resultados/` + `metricas.csv` | Yo |
| 7 | Gráfica comparativa final | Compañeros |
| 8 | Video anotado con telemetría | Compañeros |
| 9 | Artículo IEEE (≤6 págs) | Todos |
| 10 | Diapositivas (≤8) | Todos |

---

## 6. Cómo correr el pipeline

```bash
cd /home/mista/Escritorio/udea/2026-II/procesamiento-digital/trabajo1
source .venv_part2/bin/activate          # si no está activado
python src/calibrar.py                   # clic en 2 marcas de la regla
python src/main.py                       # corre todo lo demás
```

Output esperado:
```
resultados/calibracion.json
resultados/tracking.csv          (1091 filas)
resultados/cinematica.csv        (1091 filas)
resultados/modelos.csv           (1091 filas)
resultados/metricas.csv          (6 filas: theta/omega/alpha × 2 modelos)
```

---

## 7. Modelo físico (referencia rápida)

### M.A.S. (sin fricción)
```
θ̈ + ωₙ²·θ = 0         con  ωₙ = √(g/L)
θ(t)   = θ₀·cos(ωₙ·t)
ω(t)   = −θ₀·ωₙ·sin(ωₙ·t)
α(t)   = −ωₙ²·θ(t)
```

### No lineal con fricción viscosa
```
θ̈ + (b/mL²)·θ̇ + (g/L)·sin(θ) = 0
```
Resuelta con `scipy.integrate.solve_ivp` (RK45).

### Comprobaciones físicas (sección 3.1.3 del PDF)
- En extremos (θ = ±θ₀): `ω = 0`, `α_máx = ±θ₀·ωₙ²`.
- En centro (θ = 0): `α = 0`, `|v|_máx = L·θ₀·ωₙ`.
