# Guia detallada del Modulo A - Histogramas y Ecualizacion

**Taller Parte 1 - PDI (Universidad de Antioquia, 2026-II)**

Este documento explica celda por celda el contenido del notebook `parte1_taller_PDI.ipynb`, incluyendo que hace cada linea de codigo, por que se hace asi y que conceptos de PDI involucra.

---

## 1. Mapa general del notebook

El notebook tiene **11 celdas** organizadas asi:

| # | Tipo | Contenido |
|---|------|-----------|
| 0 | markdown | Cabecera y contexto del modulo |
| 1 | codigo | Imports, helpers y carga de imagen |
| 2 | markdown | Titulo del Ejercicio A.1 |
| 3 | codigo | Imagen original + histograma en grises |
| 4 | codigo | Histogramas por canal en RGB y HSV |
| 5 | markdown | Titulo del Ejercicio A.2 |
| 6 | codigo | Ecualizacion global + 4 configuraciones CLAHE |
| 7 | markdown | Pregunta 1.1 con respuesta |
| 8 | markdown | Pregunta 1.2 con respuesta |
| 9 | codigo | Demo empirica RGB vs HSV-V vs LAB-L |
| 10 | markdown | Conclusiones del modulo |

---

## 2. Celda 0 - Cabecera

```markdown
# Parte 1 - Taller Practico y Conceptual de PDI
## Modulo A: Analisis y Ecualizacion de Histogramas (7.5%)
Universidad de Antioquia - Procesamiento Digital de Imagenes - 2026-II
```

**Que hace:** Solo presenta el modulo y la imagen de trabajo (`im1.png`).

**Por que:** Es la primera celda que se ve al abrir el notebook; da contexto rapido al lector (y al profesor) sin tener que abrir el PDF.

---

## 3. Celda 1 - Configuracion inicial

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt

%matplotlib inline
```

### 3.1 Las tres librerias

- **`cv2` (OpenCV):** es la libreria principal de vision por computadora. Todas las operaciones sobre imagenes (leer, convertir a otro espacio de color, ecualizar, etc.) se hacen con funciones `cv2.*`.
- **`numpy`:** las imagenes se representan internamente como arreglos `numpy` de forma `(alto, ancho, canales)` con tipo `uint8` (enteros de 0 a 255). Cualquier operacion matricial se hace con `numpy`.
- **`matplotlib.pyplot`:** se usa unicamente para graficar (mostrar imagenes y dibujar histogramas).

### 3.2 `%matplotlib inline`

Es una "magic command" de Jupyter. Le dice al notebook que muestre las graficas de matplotlib **dentro del propio notebook** (debajo de la celda), en lugar de abrirlas en una ventana emergente. Es indispensable para que el notebook sea autocontenido.

### 3.3 El helper `mostrar()`

```python
def mostrar(img, titulo, cmap=None):
    plt.figure(figsize=(7, 5))
    if img.ndim == 3:
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(img, cmap=cmap or 'gray', vmin=0, vmax=255)
    plt.title(titulo)
    plt.axis('off')
    plt.show()
```

**Que hace:** recibe una imagen y la muestra con matplotlib.

**Detalle clave:** OpenCV lee imagenes a color en formato **BGR** (Blue, Green, Red), pero matplotlib espera **RGB**. Si no se hace la conversion, los colores se ven intercambiados (un cielo azul aparece como naranja, etc.). Por eso:

```python
cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
```

Ademas:
- `img.ndim == 3` distingue imagenes a color (3 canales) de escala de grises (2 dimensiones).
- `cmap='gray'` y `vmin=0, vmax=255` fijan la escala de grises, porque matplotlib sino la ajusta automaticamente y dos imagenes con distinta iluminacion pueden terminar viéndose igual.

### 3.4 El helper `histograma()`

```python
def histograma(img, canal=0, mascara=None):
    return cv2.calcHist([img], [canal], mascara, [256], [0, 256]).flatten()
```

**Que hace:** envuelve `cv2.calcHist` con parametros sensatos para una imagen de 8 bits.

**Parametros de `cv2.calcHist`:**

| Parametro | Valor | Significado |
|-----------|-------|-------------|
| `[img]` | la imagen | puede pasarse una lista para calcular varios histogramas a la vez |
| `[canal]` | 0, 1 o 2 | que canal se quiere medir |
| `mascara` | `None` | si se pasa una mascara binaria, solo se cuentan los pixeles dentro de ella |
| `[256]` | numero de bins | un bin por cada nivel de intensidad (0 a 255) |
| `[0, 256]` | rango | rango de intensidades a contar |

El `.flatten()` al final convierte el resultado (que es un arreglo columna de 256x1) en un vector de 256 elementos, que es lo que `plt.plot()` espera.

### 3.5 Carga de la imagen

```python
img = cv2.imread('im1.png')
assert img is not None, 'No se encontro im1.png'
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
print('Imagen:', img.shape, '| OpenCV', cv2.__version__)
```

- `cv2.imread('im1.png')` lee el archivo. Si la ruta no existe, devuelve `None`.
- El `assert` protege contra el caso "no se encontro el archivo"; si esto falla, el notebook se detiene con un mensaje claro.
- `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` convierte a escala de grises usando la formula de luminosidad perceptual: $Y = 0.299 R + 0.587 G + 0.114 B$. El ojo humano es mas sensible al verde, por eso pesa mas que el azul.
- `cv2.cvtColor(img, cv2.COLOR_BGR2HSV)` convierte al espacio HSV. En OpenCV el canal **H (Tono)** va de **0 a 179** (no de 0 a 360), porque se almacena en 8 bits. **S y V** van de 0 a 255.
- `img.shape` devuelve `(alto, ancho, canales)`, util para verificar dimensiones.

---

## 4. Celdas 2 a 4 - Ejercicio A.1: Calculo de Histogramas

### 4.1 Celda 2 - Titulo y teoria

```markdown
El histograma $h(r_k) = n_k$ cuenta cuantos pixeles tienen intensidad $r_k$.
Normalizado por el total $N$ se obtiene la PDF discreta $p(r_k) = n_k / N$.
```

**Conceptos clave:**

- **Histograma:** numero de pixeles por nivel de intensidad. Es la base de toda la estadistica de la imagen.
- **PDF normalizada:** $p(r_k) = n_k / N$ es una probabilidad real (entre 0 y 1). Si se suman todos los valores de $p$, da 1.
- **Por que importa:** la forma del histograma es un "diagnostico" instantaneo:
  - Pico a la izquierda = imagen oscura.
  - Pico a la derecha = imagen clara.
  - Pico angosto = contraste bajo.
  - Distribucion uniforme = buen contraste.

### 4.2 Celda 3 - Imagen + histograma en grises

```python
mostrar(img, 'Imagen original')

plt.figure(figsize=(8, 3))
plt.plot(histograma(gray), color='k')
plt.title('Histograma en escala de grises')
plt.xlabel('Intensidad'); plt.ylabel('N. pixeles'); plt.xlim(0, 255)
plt.grid(alpha=0.3); plt.show()

print(f'Media: {gray.mean():.1f} | Desv. estandar: {gray.std():.1f}')
print(f'Pixeles oscuros (<64): {100*np.mean(gray < 64):.1f}%')
```

**Que muestra:**

- La imagen original.
- Su histograma: en el eje X las intensidades (0-255), en el Y cuantos pixeles hay en cada una.
- Dos metricas: la **media** (intensidad promedio) y la **desviacion estandar** (que tan dispersos estan los valores).

**Como se interpreta en `im1.png`:**

- `gray.mean()` ≈ 58 (mucho menor que 128, el gris medio): la imagen es **oscura**.
- `np.mean(gray < 64)` ≈ 67%: dos tercios de los pixeles son oscuros.
- Conclusion: la imagen tiene **sombras marcadas** y es buen candidato para ecualizar.

### 4.3 Celda 4 - Histogramas RGB y HSV

```python
for i, c, n in zip(range(3), ('b', 'g', 'r'), ('B', 'G', 'R')):
    plt.plot(histograma(img, i), color=c, label=n)
```

**Que hace:** itera sobre los 3 canales de la imagen y dibuja los tres histogramas en una sola grafica con colores B, G, R.

**Detalle importante:** OpenCV carga la imagen en formato **BGR** (no RGB). Por eso el orden de los colores en el ciclo es `'b', 'g', 'r'`: canal 0 = azul, canal 1 = verde, canal 2 = rojo. Si se rotaran los colores, los histogramas seguirian siendo correctos (porque el calculo no depende del color de la linea), pero la leyenda estaria etiquetada mal.

```python
for i, c, n in zip(range(3), ('m', 'c', 'y'), ('H (Tono)', 'S (Sat.)', 'V (Brillo)')):
    plt.plot(histograma(hsv, i), color=c, label=n)
```

Misma idea pero para HSV. Usamos colores `'m'` (magenta), `'c'` (cian), `'y'` (amarillo) para que las curvas sean distinguibles de las del plot anterior.

**Interpretacion de los histogramas de `im1.png`:**

- **RGB:** los tres canales tienen formas muy parecidas y medias casi iguales. Cuando R ≈ G ≈ B en casi toda la imagen, la escena es **acromatica** (grises, marrones apagados, sin color dominante).
- **HSV:**
  - **H (Tono):** se reparte en dos zonas (tonos calidos marrones y tonos frios verdosos/azulados).
  - **S (Saturacion):** concentrada en valores bajos → imagen **poco saturada**.
  - **V (Brillo):** repite el patron del histograma de grises → escena **oscura**.

---

## 5. Celdas 5 y 6 - Ejercicio A.2: Ecualizacion Global vs CLAHE

### 5.1 Celda 5 - Marco teorico

La celda explica dos transformaciones:

**Ecualizacion global** (formula clave):

$$s_k = (L-1) \cdot \mathrm{CDF}(r_k)$$

Es decir, la intensidad de salida es proporcional a la **CDF** (funcion de distribucion acumulada) de la imagen. El resultado: el histograma de salida tiende a ser **uniforme**, lo que maximiza el contraste global.

**CLAHE** = Contrast Limited Adaptive Histogram Equalization:

1. **Local:** divide la imagen en una cuadricula de celdas (`tileGridSize`, por ej. 8x8) y ecualiza cada celda con **su propia** CDF.
2. **Limitada:** antes de calcular la CDF local, **recorta** cualquier bin del histograma que supere `clipLimit` y redistribuye el excedente. Esto acota la pendiente maxima de la CDF (y por tanto la ganancia maxima).

### 5.2 Celda 6 - Codigo

```python
eq_global = cv2.equalizeHist(gray)
```

Aplica la ecualizacion global sobre la imagen en grises. El histograma resultante es aproximadamente uniforme.

```python
configs = [(2.0, (8, 8)), (2.0, (16, 16)), (4.0, (8, 8)), (4.0, (16, 16))]
clahe_results = {}
for clip, tile in configs:
    c = cv2.createCLAHE(clipLimit=clip, tileGridSize=tile).apply(gray)
    clahe_results[f'clip={clip}, tile={tile}'] = c
```

**Que hace:** crea las 4 configuraciones de CLAHE que pide el PDF:

| clipLimit | tileGridSize | Efecto esperado |
|-----------|--------------|-----------------|
| 2.0 | (8, 8) | Realce suave, celdas grandes |
| 2.0 | (16, 16) | Realce suave, celdas pequenas |
| 4.0 | (8, 8) | Realce fuerte, celdas grandes |
| 4.0 | (16, 16) | Realce fuerte, celdas pequenas |

El patron `cv2.createCLAHE(...).apply(gray)` es importante: primero **se crea el objeto CLAHE** con los parametros deseados, y luego se aplica sobre la imagen con `.apply()`. No se puede reutilizar el mismo objeto para imagenes con `tileGridSize` diferente, hay que crear uno nuevo.

```python
imgs = [gray, eq_global] + list(clahe_results.values())
titulos = ['Original', 'Eq. global'] + list(clahe_results.keys())

plt.figure(figsize=(14, 8))
for i, (im, t) in enumerate(zip(imgs, titulos)):
    plt.subplot(2, 3, i + 1)
    plt.imshow(im, cmap='gray', vmin=0, vmax=255)
    plt.title(t, fontsize=9); plt.axis('off')
plt.tight_layout(); plt.show()
```

**Que hace:** arma una grilla 2x3 con la imagen original, la ecualizacion global y las 4 versiones de CLAHE, para comparacion visual directa.

`plt.subplot(2, 3, i+1)` significa: figura dividida en 2 filas x 3 columnas, colocar el subplot en la posicion `i+1` (se cuenta desde 1, no desde 0).

`plt.tight_layout()` ajusta automaticamente los margenes para que los titulos no se solapen.

```python
plt.figure(figsize=(9, 4))
plt.plot(histograma(gray), color='k', lw=2, label='Original')
plt.plot(histograma(eq_global), '--', color='b', label='Eq. global')
for (clip, tile), c in zip(configs, clahe_results.values()):
    plt.plot(histograma(c), label=f'CLAHE clip={clip}, tile={tile}')
```

**Que hace:** superpone los histogramas en una sola grafica para comparar como cambia la distribucion de intensidades con cada metodo.

- `lw=2` y `'--'` (linea punteada) sirven para diferenciar visualmente "Original" y "Eq. global".
- Las curvas de CLAHE comparten parametros similares, asi que se agrupan de a pares en la grafica.

**Como se interpreta el resultado:**

- **Ecualizacion global:** el histograma se "estira" hasta cubrir todo [0, 255], pero a costa de granular las zonas lisas (el ruido del sensor, antes invisible, se amplifica).
- **CLAHE con `clipLimit=2.0`:** histograma mas compacto (porque limita la pendiente), pero el contraste local es visible y los fondos lisos quedan limpios.
- **CLAHE con `clipLimit=4.0`:** histograma mas extendido, contraste mas fuerte, pero el grano en zonas lisas empieza a notarse.
- **`tileGridSize` (8,8) vs (16,16):** con celdas mas pequenas (16x16), la estadistica es mas local y se adapta mejor a variaciones regionales de iluminacion. Con celdas mas grandes (8x8), la estimacion del histograma es mas estable.

---

## 6. Celda 7 - Pregunta 1.1: Sobre-amplificacion de ruido

> Por que la ecualizacion global arruina zonas homogeneas y CLAHE no?

**Respuesta (resumen):**

En una zona homogenea, casi todos los pixeles tienen intensidades muy parecidas: la PDF tiene un **pico muy alto y estrecho**. La CDF, que es la integral de la PDF, presenta ahi un **salto casi vertical**. La pendiente $dT/dr$ de la transformacion es proporcional a $p(r)$, asi que en esa zona la pendiente es enorme: pequenas variaciones de entrada (ruido de sensor de +-2 niveles) se multiplican por esa pendiente y se convierten en grandes variaciones de salida (decenas de niveles). Resultado: una pared que antes era uniforme ahora aparece con manchas.

CLAHE resuelve esto en dos frentes:

1. **Recorte (clipping):** cualquier bin del histograma local que supere `clipLimit` se recorta antes de calcular la CDF. Asi, la pendiente maxima de la CDF local queda acotada.
2. **Localidad:** como la CDF se calcula **por celdas**, el pico de una region solo afecta su propia transformacion, no al resto de la imagen.

---

## 7. Celdas 8 y 9 - Pregunta 1.2: Canal de brillo vs RGB

### 7.1 Celda 8 - Respuesta conceptual

> Por que es mala practica ecualizar R, G, B por separado y es mejor aplicar CLAHE solo sobre V (HSV) o L (CIELAB)?

**Respuesta (resumen):**

El color percibido depende de las **proporciones** R:G:B, no de los valores absolutos. Si se aplica una ecualizacion distinta a cada canal, las razones R:G:B cambian arbitrariamente y los tonos se destruyen: aparecen **colores falsos** que no existian en la escena original.

Los espacios **HSV** y **CIELAB** resuelven esto al **separar** la informacion:

- Un canal de **luminancia** (V en HSV, L en CIELAB) que concentra el brillo.
- Canales de **crominancia** (H, S en HSV; a, b en CIELAB) que concentran el color.

Aplicar CLAHE **solo** sobre V o L redistribuye el brillo sin alterar las proporciones cromaticas, asi el tono se preserva. CIELAB ademas es **perceptualmente uniforme**: variaciones iguales de L corresponden a diferencias de brillo percibido aproximadamente iguales, asi el realce coincide con la sensibilidad del ojo humano.

### 7.2 Celda 9 - Demo empirica

```python
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# (a) Mala practica: ecualizar B, G y R por separado
b, g, r = cv2.split(img)
eq_rgb = cv2.merge([cv2.equalizeHist(b), cv2.equalizeHist(g), cv2.equalizeHist(r)])

# (b) Buena practica: CLAHE solo sobre V (HSV)
h, s, v = cv2.split(hsv)
eq_hsv = cv2.cvtColor(cv2.merge([h, s, clahe.apply(v)]), cv2.COLOR_HSV2BGR)

# (c) Buena practica: CLAHE solo sobre L (CIELAB)
lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
L, A, B = cv2.split(lab)
eq_lab = cv2.cvtColor(cv2.merge([clahe.apply(L), A, B]), cv2.COLOR_Lab2BGR)
```

**Que hace cada bloque:**

- **`cv2.split(img)`** separa los 3 canales de la imagen en 3 arreglos `numpy` independientes. Es la inversa de `cv2.merge`.
- **Bloque (a):** ecualiza cada canal B, G y R con su propia CDF global. Luego los vuelve a unir con `cv2.merge`. Resultado: colores falsos.
- **Bloque (b):**
  1. Separa HSV en H, S, V.
  2. Aplica CLAHE **solo a V**.
  3. Re-une H + S + V con la nueva V.
  4. Convierte de HSV a BGR para poder mostrarla con matplotlib.
- **Bloque (c):** misma idea pero en CIELAB, aplicando CLAHE a L.

**El truco clave** es siempre el mismo: **split → modificar solo el canal de luminancia → merge → convertir de vuelta a BGR**.

```python
plt.figure(figsize=(12, 9))
for i, (im, t) in enumerate(zip(casos, titulos)):
    plt.subplot(2, 2, i + 1)
    plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    plt.title(t, fontsize=10); plt.axis('off')
plt.tight_layout(); plt.show()
```

Muestra las 4 imagenes (original + las 3 variantes) en una grilla 2x2 para comparar visualmente el efecto de cada estrategia.

---

## 8. Celda 10 - Conclusiones

Resume los 4 puntos clave del modulo en una lista corta:

1. El histograma es la PDF discreta de las intensidades y permite diagnosticar exposicion y contraste.
2. La ecualizacion global maximiza el contraste pero sobre-amplifica el ruido.
3. CLAHE combina CDF local con clipping para acotar la ganancia.
4. En color se opera solo sobre la luminancia (V/L), nunca sobre R, G, B por separado.

---

## 9. Anexo: funciones de OpenCV clave

| Funcion | Para que se usa en este notebook |
|---------|--------------------------------|
| `cv2.imread(ruta)` | Lee una imagen de disco en BGR. Devuelve `None` si no existe. |
| `cv2.cvtColor(img, codigo)` | Cambia de espacio de color. Codigos usados: `BGR2GRAY`, `BGR2HSV`, `BGR2RGB`, `HSV2BGR`, `BGR2Lab`, `Lab2BGR`. |
| `cv2.calcHist([img], [canal], mascara, [bins], [rango])` | Calcula el histograma de un canal. Devuelve un arreglo 256x1, por eso se usa `.flatten()`. |
| `cv2.equalizeHist(gray)` | Ecualizacion global del histograma. Solo acepta imagenes de 1 canal. |
| `cv2.createCLAHE(clipLimit, tileGridSize)` | Crea un objeto CLAHE configurable. |
| `clahe.apply(img)` | Aplica el objeto CLAHE a una imagen. |
| `cv2.split(img)` | Separa los 3 canales en 3 arreglos. |
| `cv2.merge([c1, c2, c3])` | Une 3 arreglos en una sola imagen de 3 canales. |

---

## 10. Glosario rapido

- **Histograma:** distribucion del numero de pixeles por nivel de intensidad.
- **PDF (Probability Density Function):** version normalizada del histograma; sus valores suman 1.
- **CDF (Cumulative Distribution Function):** integral acumulada de la PDF. Va de 0 a 1.
- **Ecualizacion global:** transformacion de intensidades basada en la CDF de toda la imagen.
- **CLAHE:** ecualizacion adaptativa por celdas con limite de contraste.
- **Luminancia:** brillo percibido por el ojo (V en HSV, L en CIELAB, Y en YCbCr).
- **Crominancia:** informacion de color separada del brillo (H, S en HSV; a, b en CIELAB).
- **clipLimit:** parametro de CLAHE que limita la altura maxima de cada bin del histograma.
- **tileGridSize:** tamaño de la cuadricula que CLAHE usa para dividir la imagen.
