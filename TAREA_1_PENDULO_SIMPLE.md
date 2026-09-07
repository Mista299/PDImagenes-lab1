# UNIVERSIDAD DE ANTIOQUIA — FACULTAD DE INGENIERÍA
## PROCESAMIENTO DIGITAL DE IMÁGENES — TAREA 1

### Análisis Experimental del Movimiento Armónico Simple (M.A.S.) en un Péndulo Mediante Visión por Computadora

| | |
|---|---|
| **Ponderación total** | 100% \| Parte 1: Taller Teórico-Práctico PDI (30%) \| Parte 2: Proyecto Péndulo (70%) |
| **Modalidad** | Grupos de máximo 3 estudiantes |
| **Herramientas** | Python 3.x, OpenCV, NumPy, SciPy, Matplotlib |
| **Fecha de entrega** | **07 de septiembre de 2026** |

---

## 1. Introducción y objetivo general

En el campo de la ingeniería de sistemas y la computación visual, la visión por computadora no consiste solo en aplicar filtros visuales: es una disciplina matemática y algorítmica capaz de transformar una matriz de píxeles capturados por un sensor óptico en variables físicas reales (ángulos, posiciones métricas, velocidades y aceleraciones) en tiempo real.

El trabajo se estructura en dos etapas complementarias:

1. **Parte 1 — Taller Práctico y Conceptual (30%):** consolidar el dominio técnico y conceptual de las técnicas esenciales de visión: histogramas, ecualización CLAHE, segmentación en espacios de color (HSV/Lab) y operaciones morfológicas matemáticas con diversos elementos estructurantes.
2. **Parte 2 — Proyecto Práctico del Péndulo (70%):** construir un montaje experimental de un péndulo simple, grabar su oscilación libre en video bajo condiciones controladas y diseñar un pipeline completo en Python + OpenCV para extraer experimentalmente su trayectoria $\theta(t)$, velocidad angular $\omega(t)$ y aceleración $\alpha(t)$, contrastando los resultados contra el modelo físico del M.A.S. y la simulación numérica no lineal.

---

## 2. Parte 1: Taller práctico y conceptual de PDI (30%)

Esta sección debe desarrollarse y entregarse en un **Jupyter Notebook (.ipynb)** ordenado, reproducible y profusamente comentado, con celdas de código funcional y celdas de texto explicativo.

### 2.1. Módulo A: Análisis y Ecualización de Histogramas (7.5%)

El histograma representa la función de densidad de probabilidad discreta de las intensidades luminosas. En este módulo se aprende a interpretar y redistribuir el contraste para resaltar objetos de interés.

- **Ejercicio A.1 (Cálculo de Histogramas):** Cargar una imagen con contraste deficiente o sombras marcadas. Calcular y graficar su histograma global en escala de grises y los histogramas independientes por cada canal en RGB y HSV.
- **Ejercicio A.2 (Ecualización Global vs CLAHE):** Aplicar la Ecualización Global (`cv2.equalizeHist`) y la Ecualización Adaptativa con Contraste Limitado (`cv2.createCLAHE`), probando diferentes límites de contraste (`clipLimit = 2.0` y `4.0`) y tamaños de bloque (`tileGridSize = (8,8)` y `(16,16)`). Comparar visualmente los resultados e histogramas.

**Pregunta 1.1 — Sobre-amplificación de Ruido:**
¿Por qué la ecualización global tiende a arruinar zonas homogéneas (como una pared lisa de fondo), generando ruido indeseado, mientras que CLAHE logra realzar el contraste local sin sobre-amplificar el fondo? Explique a nivel de la función de distribución acumulada (CDF).

**Pregunta 1.2 — Canal de Brillo vs RGB:**
¿Por qué en procesamiento de color es una pésima práctica ecualizar los canales R, G y B de forma independiente, y resulta mucho más adecuado aplicar CLAHE únicamente sobre el canal de brillo/luminancia ($V$ en HSV o $L$ en CIELAB)?

---

### 2.2. Módulo B: Espacios de Color y Segmentación (7.5%)

En el espacio RGB tradicional, un cambio de iluminación o una sombra altera simultáneamente los valores de R, G y B. Desacoplar la crominancia (color puro) de la luminancia (brillo) es indispensable para una visión robusta.

- **Ejercicio B.1 (Descomposición de Canales):** Descomponer una imagen con varios marcadores de color en sus canales individuales en Escala de Grises, HSV y CIELAB. Visualizar cada canal como una imagen monocromática.
- **Ejercicio B.2 (Segmentación RGB vs HSV):** Segmentar un marcador de color usando umbralización por rangos (`cv2.inRange`). Comparar la máscara obtenida en RGB (definiendo límites en R, G, B) contra la máscara obtenida en HSV (definiendo límites en H y S). Simular una sombra y evaluar cuál método mantiene el objeto sin perderse.

**Pregunta 1.3 — Invarianza del Matiz:**
¿Por qué el canal $H$ (Hue / Matiz) en el espacio HSV ofrece inmunidad frente a sombras y cambios moderados de iluminación en comparación con el espacio RGB?

**Pregunta 1.4 — Indeterminación en HSV:**
¿En qué zonas del espacio de color el canal $H$ se vuelve matemáticamente indeterminado o ruidoso? *(Pista: analice qué ocurre cuando la Saturación $S$ o el Brillo $V$ son muy cercanos a cero).*

> **Nota:** El documento original hace referencia a un "Módulo C: Bordes y Gradientes (5.0%)" — visible únicamente en la rúbrica final (Sobel, Laplaciano, Canny con histéresis, Pregunta 1.5) — pero su enunciado detallado no aparece en el cuerpo del PDF proporcionado. Verifica con el enunciado original o con el profesor si falta contenido de esa sección.

---

### 2.4. Módulo D: Morfología Matemática y Elementos Estructurantes (10.0%)

La morfología matemática limpia las imperfecciones de las máscaras binarias usando una sonda geométrica (kernel o elemento estructurante).

- **Ejercicio D.1 (Erosión y Dilatación):** Aplicar Erosión y Dilatación sobre una máscara binaria ruidosa, evaluando el efecto de 1, 2 y 4 iteraciones.
- **Ejercicio D.2 (Apertura y Cierre):** Demostrar cómo la Apertura (`cv2.MORPH_OPEN`) elimina puntos blancos aislados (ruido sal) en el fondo y cómo el Cierre (`cv2.MORPH_CLOSE`) sella huecos negros internos (ruido pimienta) dentro del objeto.
- **Ejercicio D.3 (Morfología Avanzada):** Aplicar Gradiente Morfológico, Top-Hat (sombrero blanco) y Black-Hat (sombrero negro). Describir qué tipo de detalles resalta cada operación.
- **Ejercicio D.4 (Estudio de Kernels):** Comparar sistemáticamente 3 geometrías de elementos estructurantes mediante `cv2.getStructuringElement`: Rectangular (`MORPH_RECT`), Elíptico (`MORPH_ELLIPSE`) y Cruz (`MORPH_CROSS`), evaluando tamaños 3x3, 5x5, 9x9 y 15x15. Mostrar una matriz visual comparativa.

**Pregunta 1.6 — Kernel Elíptico vs Rectangular:**
¿Por qué para segmentar y calcular el centroide de un marcador esférico circular es mucho más preciso usar un elemento estructurante elíptico que uno rectangular?

**Pregunta 1.7 — Reconexión de Varillas Delgadas:**
Si durante el seguimiento del péndulo la cuerda o varilla delgada sufre discontinuidades (pequeñas roturas de 2 a 4 píxeles) por reflejos, ¿qué operación morfológica y qué tipo/tamaño de kernel recomendaría para reconectarla sin deformar la masa?

**Pregunta 1.8 — Aplicaciones de Top-Hat:**
¿En qué escenarios industriales (como inspección de pistas en placas PCB) o biomédicos resulta fundamental el uso de las transformadas Top-Hat y Black-Hat?

---

### Figura 1 — Pipeline general de Procesamiento Digital de Imágenes y Visión por Computador

Flujo secuencial de transformación desde el fotograma crudo hasta la estimación y validación de las variables cinemáticas:

```
[1. Preprocesamiento      [2. Umbralización     [3. Morfología          [4. Momentos y        [5. Cinemática,
 y Color HSV]        -->   y cv2.inRange]  -->   (Apertura + Cierre)] -> Centroides (x,y)] --> EDO y Telemetría]

 Filtro Gaussiano          Máscara binaria        Kernel Elíptico         Ángulo θ(t)            ω(t), α(t)
 Espacio HSV / Lab         por rangos de color     Supresión de ruido     atan2(dx, -dy)          Simulación RK45
```

---

## 3. Parte 2: Proyecto práctico — Seguimiento y análisis del péndulo común (70%)

En esta fase se construye el montaje experimental, se registra el video y se programa en Python el seguimiento automático de la masa del péndulo, contrastando los resultados experimentales con las leyes de la física clásica.

### 3.1. Modelo físico y fórmulas matemáticas del péndulo simple

Un péndulo simple está formado por una masa $m$ suspendida de un punto fijo superior (**Pivote** $O(x_0, y_0)$) mediante una cuerda de longitud $L$. Al separarlo un ángulo inicial $\theta_0$ de la vertical y soltarlo sin impulso inicial, oscila bajo la gravedad.

#### Figura 2 — Esquema físico y sistema de referencia

**Sistema de cámara (px):**
- Origen $(0,0)$ en la esquina superior; eje $X$ positivo hacia la derecha, eje $Y$ positivo hacia abajo.
- Marcador A (Pivote): origen fijo $O(x_0, y_0)$.
- Marcador B (Masa): centroide móvil $P(x(t), y(t))$, describe una trayectoria circular de radio $L$.
- Ángulo: $\theta = \operatorname{atan2}(x - x_0,\; y - y_0)$
- $\theta = 0$ corresponde a la posición de equilibrio (vertical).
- Peso: $P = m \cdot g$ ; Tensión de la cuerda: $T$.

#### 1. Ecuación diferencial dinámica general (modelo real con fricción viscosa)

$$
\theta''(t) + \left(\frac{b}{m L^2}\right)\theta'(t) + \left(\frac{g}{L}\right)\sin(\theta(t)) = 0
$$

donde $b$ es el coeficiente de fricción viscosa.

#### 2. Fórmulas teóricas del M.A.S. para pequeñas oscilaciones ($\theta < 15°$)

Para oscilaciones pequeñas se aproxima $\sin(\theta) \approx \theta$:

- **Frecuencia angular natural:**
$$
\omega_n = \sqrt{\frac{g}{L}} \quad [\text{rad/s}]
$$

- **Período de oscilación:**
$$
T = 2\pi \sqrt{\frac{L}{g}} \quad [\text{s}]
$$

- **Posición angular:**
$$
\theta(t) = \theta_0 \cos(\omega_n t) \quad [\text{rad}]
$$

- **Velocidad angular:**
$$
\omega(t) = -\theta_0 \, \omega_n \sin(\omega_n t) \quad [\text{rad/s}]
$$

- **Aceleración angular:**
$$
\alpha(t) = -\theta_0 \, \omega_n^2 \cos(\omega_n t) \quad [\text{rad/s}^2]
$$

- **Velocidad lineal tangencial:**
$$
v(t) = L \cdot \omega(t) \quad [\text{m/s}]
$$

#### 3. Comprobación física en puntos notables de la trayectoria

**a) En los extremos de oscilación ($\theta = \pm\theta_0$):**
- La masa se detiene momentáneamente: $v = 0 \ \text{m/s}$, $\omega = 0 \ \text{rad/s}$
- La aceleración es máxima: $\alpha_{\text{máx}} = \pm \theta_0 \cdot \omega_n^2$

**b) En el punto central de equilibrio ($\theta = 0$ rad):**
- La aceleración tangencial se anula: $a_t = 0 \ \text{m/s}^2$
- La velocidad alcanza su valor pico máximo: $v_{\text{máx}} = L \cdot \theta_0 \cdot \omega_n$

#### 4. Métricas de comparación experimental

- **Error Cuadrático Medio (RMSE):**
$$
\text{RMSE} = \sqrt{\frac{1}{N}\sum_{t=1}^{N}\left(\theta_{\text{exp}}(t) - \theta_{\text{teor}}(t)\right)^2}
$$

- **Calibración métrica:**
$$
k = \frac{0.30 \ \text{m}}{D_{\text{píxeles}}} \quad [\text{m/px}]
$$

---

### 3.2. Guía de montaje y grabación del video

> **[CONSEJO PRÁCTICO PARA INGENIERÍA] RECOMENDACIÓN FUNDAMENTAL: FONDO HOMOGÉNEO Y UNIFORME**
> Utilicen un fondo de color plano y uniforme (cartulina o tela verde chroma, azul, blanca o negra mate, sin arrugas ni sombras). Un fondo homogéneo hace que la umbralización por color en HSV funcione perfectamente al primer intento, ahorrándoles horas de depuración de ruido.

#### Figura 3 — Configuración del plano ortogonal de cámara, fondo uniforme y calibración métrica

- Fondo homogéneo (cartulina o tela verde/azul mate sin arrugas), con:
  - Marcador A (pivote, azul) en la parte superior.
  - Marcador B (masa, naranja) colgando de una cuerda blanca.
  - Regla patrón de calibración de 30 cm visible en el plano.
- Cámara en trípode, alineada en **línea óptica ortogonal (90°)** respecto al plano de oscilación, a una distancia $D = 1.5$ a $2.0$ m.

**Checklist de montaje y grabación:**

1. **Fondo uniforme:** cartulina o tela verde/azul mate, sin arrugas ni sombras.
2. **Marcadores A y B:** colores saturados y contrastantes (azul y naranja).
3. **Calibración métrica:** regla en el mismo plano focal de oscilación.
4. **Iluminación difusa:** luces indirectas para eliminar reflejos y sombras.
5. **Liberación limpia:** soltar el péndulo desde $\theta_0 = 10°$ a $15°$ sin empuje.

**Especificaciones de captura:**

- Plano frontal fijo (sin mover la cámara).
- Resolución mínima: **1080p** (1920×1080).
- Frecuencia: **60 fps** (o 30 fps).
- Enfoque y exposición: manual / bloqueado.
- Distancia $D$ = 1.5 a 2.0 metros.

**Detalles adicionales del montaje:**

- **Plano Frontal Ortogonal:** cámara en trípode totalmente fija, perpendicular (90°) al plano donde oscila el péndulo. La altura del lente debe coincidir con el centro del recorrido para evitar distorsiones de perspectiva.
- **Marcadores de Alto Contraste:** Marcador A (azul o rojo) en el pivote de giro superior $O(x_0, y_0)$ y Marcador B (naranja o verde neón) en el centro de la masa oscilante $P(x(t), y(t))$.
- **Calibración Métrica:** pegar una regla graduada (ej. 30 cm) en el mismo plano focal de la oscilación para calcular el factor de escala: $k = 0.30 \ \text{m} / D_{\text{píxeles}}$ [m/px].
- **Cámara y FPS:** mínimo 1080p a 60 fps (o 30 fps). Bloquear autoenfoque y exposición automática para evitar parpadeos (flicker).
- **Liberación Limpia:** soltar el péndulo desde un ángulo inicial $\theta_0$ entre 10° y 15° con cuidado, sin empujarlo lateralmente (para que oscile en un solo plano bidimensional).

---

### 3.3. Pipeline de procesamiento de imágenes (OpenCV + Python)

El programa en Python deberá realizar las siguientes etapas fotograma a fotograma:

| Paso | Descripción |
|---|---|
| **Paso 1 — Calibración de Escala y Pivote** | Medir la longitud en píxeles de la regla de 30 cm y obtener $k$ [m/px]. Registrar las coordenadas estáticas del pivote $O(x_0, y_0)$. |
| **Paso 2 — Preprocesamiento y Espacio HSV** | Convertir cada cuadro a HSV y aplicar filtrado Gaussiano (`cv2.GaussianBlur`) para reducir ruido de alta frecuencia. |
| **Paso 3 — Máscara Binaria** | Aislar el marcador de la masa mediante `cv2.inRange` con los límites calibrados $[H_{\min}, S_{\min}, V_{\min}]$ y $[H_{\max}, S_{\max}, V_{\max}]$. |
| **Paso 4 — Limpieza Morfológica** | Aplicar Apertura con kernel elíptico 5x5 para eliminar ruido puntual en el fondo, seguido de un Cierre para rellenar el marcador. |
| **Paso 5 — Centroide de la Masa** | Detectar contornos (`cv2.findContours`), elegir el contorno de mayor área y extraer el centroide $P(x(t), y(t))$ usando momentos de imagen: $c_x = M_{10}/M_{00}$, $c_y = M_{01}/M_{00}$. |
| **Paso 6 — Ángulo Instantáneo** | Calcular el ángulo experimental con respecto a la vertical: $\theta_{\text{exp}}(t) = \operatorname{atan2}(x(t) - x_0,\; y(t) - y_0)$ en radianes. |
| **Paso 7 — Derivación Numérica Suavizada** | Con el vector temporal $t = n / \text{FPS}$, calcular $\omega_{\text{exp}}(t) = \dfrac{d\theta}{dt}$ y $\alpha_{\text{exp}}(t) = \dfrac{d^2\theta}{dt^2}$ mediante derivadas numéricas. Aplicar un filtro de regularización (`scipy.signal.savgol_filter`) para eliminar la amplificación de ruido. |

---

### 3.4. Comparación experimental vs. teórica y métricas de error

En el informe y el Jupyter Notebook deben presentarse los siguientes análisis comparativos:

1. **Gráfica de Ángulo vs Tiempo:** $\theta_{\text{exp}}(t)$ vs $\theta_{\text{teórico}}(t)$ superpuestas, demostrando la coincidencia de frecuencia y desfase.
2. **Gráfica de Velocidad vs Tiempo:** $\omega_{\text{exp}}(t)$ vs $\omega_{\text{teórico}}(t)$ superpuestas.
3. **Gráfica de Aceleración vs Tiempo:** $\alpha_{\text{exp}}(t)$ vs $\alpha_{\text{teórico}}(t)$ superpuestas.
4. **Retrato de Espacio de Fases:** gráfica en el plano $(\theta, \omega)$ comparando la elipse teórica del M.A.S. con la espiral observada experimentalmente debido al amortiguamiento.
5. **Discusión de Fuentes de Error:** explicación física de las discrepancias — amortiguamiento por resistencia del aire, fricción en el hilo/pivote, discretización de píxeles y pequeñas no linealidades.

**Métricas cuantitativas de error:**
$$
\text{RMSE} = \sqrt{\frac{1}{N}\sum_{t=1}^{N}\left(\theta_{\text{exp}}(t) - \theta_{\text{teor}}(t)\right)^2}
$$

---

### 3.5. Video procesado con telemetría en pantalla

El programa exportará un video anotado (.mp4 o .avi) con:

- **Trayectoria:** dibujo de la trayectoria continua (estela) que recorre la masa.
- **Geometría:** línea que une el pivote con la masa, y línea vertical punteada de referencia ($\theta = 0$).
- **Telemetría en vivo:** panel de texto en la esquina superior con:
  - Tiempo $t$ [s]
  - Ángulo actual $\theta$ [° y rad]
  - Velocidad angular $\omega$ [rad/s]
  - Aceleración angular $\alpha$ [rad/s²]
  - FPS en tiempo real

---

## 4. Entregables del proyecto

1. **Notebook del Taller (Parte 1 — 30%):** Jupyter Notebook ejecutable (.ipynb) con los módulos de histogramas, color, bordes, morfología y respuestas conceptuales justificadas.
2. **Video Original Grabado:** video sin editar (.mp4) con la vista ortogonal, fondo uniforme y regla patrón visible.
3. **Video Procesado con Telemetría:** video exportado por OpenCV con la trayectoria dibujada y el panel de telemetría sobreimpreso.
4. **Código Fuente del Proyecto:** scripts en Python (.py o .ipynb) documentados, modulares y con instrucciones claras de ejecución.
5. **Informe en Formato IEEE:** artículo técnico (máximo 6 páginas) con Resumen, Introducción y Modelado Físico, Metodología de PDI, Resultados con Gráficas Comparativas, Análisis de Error y Conclusiones.
6. **Diapositivas de Sustentación:** presentación ejecutiva (PowerPoint o PDF, máximo 8 diapositivas) para sustentación en clase.

---

## 5. Rúbrica y criterios de evaluación

| Componente / Criterio | Aspectos a evaluar y desempeño esperado | Peso |
|---|---|---|
| **Parte 1: Histogramas y Ecualización** | Cálculo de histogramas, implementación Global vs CLAHE, calidad gráfica y respuestas conceptuales 1.1 y 1.2. | **7.5%** |
| **Parte 1: Espacios de Color** | Descomposición de canales, segmentación HSV vs RGB ante sombras y respuestas conceptuales 1.3 y 1.4. | **7.5%** |
| **Parte 1: Bordes y Gradientes** | Implementación de Sobel, Laplaciano, Canny con histéresis y respuesta conceptual 1.5. | **5.0%** |
| **Parte 1: Morfología Matemática** | Erosión, dilatación, apertura, cierre, top-hat/black-hat, comparación de kernels (rect, elipse, cruz) y respuestas 1.6, 1.7 y 1.8. | **10.0%** |
| **Parte 2: Montaje y Grabación** | Uso de plano ortogonal estático, fondo uniforme, marcadores A y B nítidos, calibración métrica y estabilidad. | **5.0%** |
| **Parte 2: Pipeline de PDI y Seguimiento** | Segmentación robusta en HSV, filtrado morfológico adecuado, cálculo preciso del centroide y ángulo instantáneo $\theta(t)$. | **30.0%** |
| **Parte 2: Modelado, Simulación y Validación** | Derivación numérica suavizada ($\omega$, $\alpha$), comprobación de extremos y centro, gráficas superpuestas exp vs teor, espacio de fases y RMSE. | **25.0%** |
| **Parte 2: Video Anotado, Informe y Sustentación** | Calidad del video con telemetría en tiempo real, rigor del informe IEEE (máx. 6 págs.), diapositivas y dominio conceptual en sustentación. | **10.0%** |
| **TOTAL** | | **100%** |

---

*Documento convertido desde el PDF original "TAREA_1_PENDULO_SIMPLE.pdf" (Universidad de Antioquia — Facultad de Ingeniería). Las fórmulas matemáticas se presentan en notación LaTeX ($\LaTeX$) para su correcta interpretación por humanos y agentes de IA. Las Figuras 1, 2 y 3 del original (diagramas) se han transcrito como descripciones estructuradas/tablas equivalentes, ya que son esquemas gráficos y no texto extraíble literal.*
