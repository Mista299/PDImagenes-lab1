# Fase 0 — Reporte de inspección del video

**Video:** `pendulo.mp4` (1080 × 1920, 25 fps, 43.64 s, 1091 frames, H.264)
**Inspección realizada:** `src/inspeccionar_video.py` + `src/tracking_preliminar.py`

## Hallazgos visuales (frames muestreados en `figs/inspeccion/`)

| t [s] | Posición de la bola | Observación |
|---|---|---|
| 0.0 | Derecha-abajo | Extremo derecho; cuerda entra por borde superior derecho |
| 5.0 | Izquierda-abajo | Extremo izquierdo; cuerda entra por borde superior izquierdo |
| 10.0 | Derecha-abajo | Vuelta al extremo derecho (medio período) |
| 15.0 | Izquierda-medio | Pasada por el centro o cerca del extremo izquierdo |
| 20.0 | Derecha-abajo | Extremo derecho |
| 25.0 | Centro-abajo | Cerca del equilibrio (θ≈0) |
| 30.0 | Lado derecho | Oscilando |
| 35.0 | Centro-derecha | Oscilando |
| 40.0 | Izquierda-abajo | Extremo izquierdo |

## Hallazgos técnicos

| Aspecto | Valor | Implicación para el pipeline |
|---|---|---|
| Resolución | 1080 × 1920 vertical | El plano de oscilación es horizontal respecto al frame (la cámara está en retrato) |
| Orientación | Vertical / retrato | **No rotar** el frame; mantener ejes nativos (`x` horizontal, `y` vertical hacia abajo) |
| FPS | 25 | Por debajo de los 60 ideales → Savitzky-Golay con `window_length` ≥ 25 |
| Duración | 43.64 s | Suficiente para ~15 períodos de oscilación |
| **Marcador de masa** | **Bola roja** (no naranja) | Segmentación HSV con dos rangos para rojo (H<10 y H>170) |
| **Marcador de pivote** | **No hay marcador visible** | Hay que inferirlo geométricamente: intersección de la cuerda |
| **Cuerda** | Hilo oscuro visible | Aproximadamente vertical en el centro; tangente al pivote en cada extremo |
| **Fondo** | Tela verde chroma | HSV: descartar `H ∈ [35, 85]` y dejar pasar rojo |
| **Sombra** | Presente en algunas zonas | HSV robusto ya que la sombra no afecta el canal H |
| **Pivote estimado** | En o por encima del borde superior del frame, cerca de x≈540 | La cuerda “desaparece” por arriba; calcularemos pivote por intersección de cuerdas |
| Regla patrón | Cinta métrica visible al pie (≈ 14 cm de ancho visible) | Calibración métrica posible; mide ~14 cm de ancho en cuadro. Hay que detectar marcas cada 1 cm |
| **Período estimado** | T ≈ 2.88 s | Estimado por cruces por cero de x(t) |
| **Longitud inferida** | L ≈ 2.06 m | Vía `L = g·T²/(4π²)`; verificable con regla |

## Decisiones de diseño ajustadas

1. **Detección del pivote:** usaré la **intersección de líneas de la cuerda** detectadas por Hough Line Transform en al menos dos frames en extremos opuestos. Si el pivote queda fuera del frame, extrapolaré.

2. **Marcador de masa:** segmentaré el **rojo** con doble rango HSV (`H ∈ [0,10] ∪ [170,180]`, `S ≥ 100`, `V ≥ 60`).

3. **Calibración métrica:** mediré la separación entre dos marcas conocidas de la cinta (cada 1 cm = 10 mm) en píxeles. Necesito al menos 5 cm visibles para que la calibración sea robusta.

4. **Filtros temporales:** Savitzky-Golay con `window_length = 31`, `polyorder = 3`, aplicado a `θ(t)` antes de derivar.

5. **Convención angular:** `θ = atan2(x − x₀, y − y₀)` (como especifica la tarea). Coincide con lo que se observa (bola a la derecha → θ > 0; a la izquierda → θ < 0).

6. **Validación física inmediata:** dado el `T ≈ 2.88 s` observado y `L ≈ 2 m`, verificaremos que `ωₙ ≈ 2π/T ≈ 2.18 rad/s` y `g/L ≈ 4.76` produzca una frecuencia natural coherente.

## Estado del proyecto

- ✅ Estructura de carpetas creada
- ✅ Entorno virtual con OpenCV, NumPy, SciPy, Matplotlib, Pandas, tqdm instalado
- ✅ Inspección visual completada (10 frames)
- ✅ Tracking preliminar funcional con HSV+contornos (273 detecciones)
- ⏳ Pendiente: calibración métrica + pivote + pipeline completo + derivadas + comparación + video anotado
