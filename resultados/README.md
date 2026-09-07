# resultados/

Datos generados por el pipeline de la Parte 2 del proyecto del péndulo.
Todos los archivos se regeneran corriendo:

```bash
cd /home/mista/Escritorio/udea/2026-II/procesamiento-digital/trabajo1
source .venv_part2/bin/activate
python src/calibrar.py   # una vez, requiere 2 clics en la cinta métrica
python src/main.py       # corre el resto (~1 min)
```

## Archivos

### `calibracion.json`
Parámetros geométricos del montaje.

| Campo | Significado | Uso |
|---|---|---|
| `pivote_xy_px` | Coordenadas (x, y) del pivote en píxeles | Para el video: dibujar la línea vertical de referencia y la línea pivote→masa |
| `L_px` | Distancia pivote-masa en píxeles | Radio de la trayectoria circular |
| `k_m_por_px` | Factor de escala metros/píxel | Para el video: convertir píxeles a metros |
| `L_m` | Longitud L en metros (inferida del período) | Parámetro físico del péndulo |

### `modelo_params.json`
Parámetros ajustados de los modelos.

| Campo | Valor | Significado |
|---|---|---|
| `theta0_rad` / `theta0_deg` | ej. 0.289 / 16.6° | Amplitud inicial (medida del primer pico) |
| `omega_n_rad_s` | ej. 4.49 | Frecuencia natural del M.A.S. |
| `T_MAS_s` | ej. 1.400 | Período teórico |
| `L_m` | ej. 0.487 | Longitud inferida del período |
| `m_kg` | 0.1 | Masa asumida de la bola |
| `b_opt_Nms_rad` | ej. 0.0008 | Coeficiente de fricción ajustado |
| `rmse_sim_rad` | ej. 0.109 | RMSE de la simulación vs experimental |
| `t_peak_s` | ej. 0.08 | Tiempo del primer pico usado como origen |

### `tracking.csv`
Centroide de la bola en cada frame (paso 6 del PDF).

| Columna | Unidad | Descripción |
|---|---|---|
| `t_s` | s | Tiempo desde el inicio del video |
| `x_px` | px | Coordenada x del centroide |
| `y_px` | px | Coordenada y del centroide |

1091 filas (todos los frames detectados).

### `cinematica.csv`
Cinemática experimental suavizada (paso 7 del PDF).

| Columna | Unidad | Descripción |
|---|---|---|
| `t_s` | s | Tiempo |
| `theta_rad` | rad | `atan2(x - x₀, y - y₀)` suavizado con Savitzky-Golay |
| `omega_rad_s` | rad/s | `dθ/dt` por gradiente |
| `alpha_rad_s2` | rad/s² | `d²θ/dt²` por gradiente |

Grilla uniforme a 25 Hz.

### `modelos.csv`
Señales teóricas: M.A.S. y simulación no lineal con fricción (sección 3.4 del PDF).

| Columna | Unidad | Descripción |
|---|---|---|
| `t_s` | s | Tiempo (origen en el primer pico experimental) |
| `theta_teo_rad` | rad | `θ₀·cos(ωₙ·t)` |
| `omega_teo_rad_s` | rad/s | `-θ₀·ωₙ·sin(ωₙ·t)` |
| `alpha_teo_rad_s2` | rad/s² | `-ωₙ²·θ(t)` |
| `theta_sim_rad` | rad | Solución numérica EDO con fricción |
| `omega_sim_rad_s` | rad/s | Velocidad angular de la simulación |
| `alpha_sim_rad_s2` | rad/s² | Aceleración angular de la simulación |

### `metricas.csv`
Tabla de errores (sección 3.4 del PDF).

| Columna | Descripción |
|---|---|
| `variable` | `theta`, `omega` o `alpha` |
| `modelo` | `MAS` (sin fricción) o `no_lineal_friccion` |
| `RMSE` | Error cuadrático medio en rad (o rad/s, rad/s²) |
| `MAE` | Error absoluto medio |
| `Pearson` | Correlación (1 = perfecto) |
| `lag_s` | Desfase temporal del máximo de correlación cruzada |

## Cómo usar estos datos

### Para el video anotado (compañero)

```python
import pandas as pd, json
import cv2
import numpy as np

# 1. Cargar calibración
cal = json.load(open('resultados/calibracion.json'))
x0, y0 = cal['pivote_xy_px']
k = cal['k_m_por_px']

# 2. Cargar cinemática
df = pd.read_csv('resultados/cinematica.csv')

# 3. Cargar video
cap = cv2.VideoCapture('pendulo.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
fps = 25  # confirmado

# 4. Por cada frame, dibujar:
#    - trayectoria (estela) con los últimos N centroides
#    - línea pivote (x0, y0) → bola (x_px, y_px)
#    - línea vertical punteada en x=x0
#    - panel de telemetría con theta, omega, alpha
```

### Para la gráfica comparativa (compañero)

```python
import pandas as pd
import matplotlib.pyplot as plt

df_c = pd.read_csv('resultados/cinematica.csv')
df_m = pd.read_csv('resultados/modelos.csv')

t = df_c['t_s'].values
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(t, df_c['theta_rad'], 'b-', label='experimental', lw=1)
ax.plot(t, df_m['theta_teo_rad'], 'r-', label='M.A.S.')
ax.plot(t, df_m['theta_sim_rad'], 'g-', label='no lineal + fricción')
ax.set_xlabel('t [s]')
ax.set_ylabel(r'$\theta$ [rad]')
ax.legend()
ax.grid(alpha=0.3)
```

### Para el artículo IEEE y diapositivas

Datos para citar en el informe:
- `metricas.csv` → tabla de comparación cuantitativa
- `modelo_params.json` → parámetros físicos ajustados
- `calibracion.json` → datos del montaje
- `figs/validacion_final.png` → gráfica de comparación (θ, ω, α vs t + espacio de fases)
