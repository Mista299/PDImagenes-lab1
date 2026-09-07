# resultados/

Datos generados por el pipeline de la Parte 2 del proyecto del péndulo.
Todos los archivos se regeneran corriendo:

```bash
cd /home/mista/Escritorio/udea/2026-II/procesamiento-digital/trabajo1
source .venv_part2/bin/activate
python src/calibrar.py   # una vez, requiere 2 clics en la cinta métrica
python src/main.py       # corre el resto (~1 min)
```

## ⚠️ Unidades

Todos los ángulos están en **radianes** (no grados). Las velocidades y aceleraciones angulares también.

| Magnitud | Unidad en los CSV/JSON | Cómo convertir a grados |
|---|---|---|
| `theta_*` | rad | multiplicar por `180/π` |
| `omega_*` | rad/s | multiplicar por `180/π` → grados/s |
| `alpha_*` | rad/s² | multiplicar por `180/π` → grados/s² |
| `x_px, y_px` | píxeles | solo convertir si necesitas metros (× `k_m_por_px`) |
| `t_s` | segundos | — |
| `L_m` | metros | — |
| `b` | N·m·s/rad | — |
| `k_m_por_px` | metros/píxel | — |

> Para visualizar en grados en las gráficas, multiplicar las columnas `theta_*` por `180/π` antes de graficar. El pipeline entrega radianes (unidades SI) por consistencia con las fórmulas del enunciado.

## Archivos

### `calibracion.json`
Parámetros geométricos del montaje.

| Campo | Unidad | Significado | Uso |
|---|---|---|---|
| `pivote_xy_px` | px | Coordenadas del pivote en píxeles | Para el video: dibujar la línea vertical de referencia y la línea pivote→masa |
| `L_px` | px | Distancia pivote-masa en píxeles | Radio de la trayectoria circular |
| `k_m_por_px` | m/px | Factor de escala metros/píxel | Para el video: convertir píxeles a metros |
| `L_m_clicks` | m | Longitud L en metros (de los clics en la regla) | Parámetro físico del péndulo |
| `L_target_m` | m | L inferida del período (`g·T²/(4π²)`) | Referencia para comparación |
| `T_exp_s` | s | Período medido del video | Para calcular `L_target_m` |
| `T_ceros_s` | s | Período por cruces por cero | Método principal |
| `T_auto_s` | s | Período por autocorrelación | Verificación |

### `modelo_params.json`
Parámetros ajustados de los modelos.

| Campo | Unidad | Significado |
|---|---|---|
| `theta0_rad` | rad | Amplitud inicial (medida del primer pico) |
| `theta0_deg` | grados | Misma amplitud en grados |
| `omega_n_rad_s` | rad/s | Frecuencia natural del M.A.S. |
| `T_MAS_s` | s | Período del M.A.S. (= T_exp medido) |
| `L_m_clicks` | m | Longitud calibrada con regla |
| `L_target_m` | m | Longitud inferida del período |
| `diferencia_porcentaje` | % | Discrepancia entre las dos |
| `m_kg` | kg | Masa asumida de la bola |
| `b_opt_Nms_rad` | N·m·s/rad | Coeficiente de fricción ajustado |
| `rmse_sim_rad` | rad | RMSE de la simulación vs experimental |
| `t_peak_s` | s | Tiempo del primer pico usado como origen |

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
| `theta_teo_rad` | rad | `θ₀·cos(ωₙ·t)` (M.A.S. sin fricción) |
| `omega_teo_rad_s` | rad/s | `-θ₀·ωₙ·sin(ωₙ·t)` |
| `alpha_teo_rad_s2` | rad/s² | `-ωₙ²·θ(t)` |
| `theta_sim_rad` | rad | Solución numérica EDO con fricción |
| `omega_sim_rad_s` | rad/s | Velocidad angular de la simulación |
| `alpha_sim_rad_s2` | rad/s² | Aceleración angular de la simulación |

### `metricas.csv`
Tabla de errores (sección 3.4 del PDF). Las unidades dependen de la variable:

| `variable` | `RMSE` y `MAE` | `Pearson` | `lag_s` |
|---|---|---|---|
| `theta` | rad | adimensional | s |
| `omega` | rad/s | adimensional | s |
| `alpha` | rad/s² | adimensional | s |

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
fps = 25  # confirmado

# 4. Por cada frame, dibujar:
#    - trayectoria (estela) con los últimos N centroides
#    - línea pivote (x0, y0) → bola (x_px, y_px)
#    - línea vertical punteada en x=x0
#    - panel de telemetría con theta, omega, alpha (recordar: en radianes)
```

### Para la gráfica comparativa (compañero)

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df_c = pd.read_csv('resultados/cinematica.csv')   # columnas en radianes
df_m = pd.read_csv('resultados/modelos.csv')

t = df_c['t_s'].values
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(t, np.degrees(df_c['theta_rad']), 'b-', label='experimental', lw=1)
ax.plot(t, np.degrees(df_m['theta_teo_rad']), 'r-', label='M.A.S.')
ax.plot(t, np.degrees(df_m['theta_sim_rad']), 'g-', label='no lineal + fricción')
ax.set_xlabel('t [s]')
ax.set_ylabel(r'$\theta$ [°]')   # en grados para visualizar
ax.legend()
ax.grid(alpha=0.3)
```

### Para el artículo IEEE y diapositivas

Datos para citar en el informe:
- `metricas.csv` → tabla de comparación cuantitativa
- `modelo_params.json` → parámetros físicos ajustados
- `calibracion.json` → datos del montaje
- `figs/validacion_final.png` → gráfica de comparación (θ, ω, α vs t + espacio de fases)
