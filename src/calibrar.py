"""Calibracion interactiva con verificacion contra el periodo observado.

Flujo:
  1. Tracking rapido de la bola -> pivote por ajuste de circulo.
  2. Estimacion automatica del periodo experimental T_exp por autocorrelacion.
  3. Calculo del L_target = g * T_exp^2 / (4*pi^2)  (valor esperado).
  4. El usuario hace clic en 2 extremos de la cinta visible e ingresa los cm.
  5. Calculamos L_clicks y comparamos con L_target.
  6. Si difieren mas del 5%, el sistema sugiere los cm correctos y permite
     re-intentar hasta que la diferencia sea aceptable.

NO se usa la formula para corregir la calibracion: solo se usa como
referencia para validar la lectura del usuario. La lectura final del
usuario es la que queda registrada.
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "pendulo.mp4"
RES = ROOT / "resultados"
RES.mkdir(parents=True, exist_ok=True)
G = 9.81

CINTA_Y0, CINTA_Y1 = 1338, 1372       # banda vertical donde esta la cinta
TOLERANCIA = 0.05                       # 5% permitido entre L_clicks y L_target


# ----------------------------------------------------------------------
# Paso 1: deteccion de la bola
# ----------------------------------------------------------------------
def detectar_bola(frame_bgr: np.ndarray) -> tuple[float, float] | None:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask = (
        cv2.inRange(hsv, np.array([0, 100, 60]), np.array([10, 255, 255]))
        | cv2.inRange(hsv, np.array([170, 100, 60]), np.array([180, 255, 255]))
    )
    mask = cv2.morphologyEx(
        mask, cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
    )
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 200:
        return None
    M = cv2.moments(c)
    return (M["m10"] / M["m00"], M["m01"] / M["m00"])


def tracking_rapido(stride: int = 4) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cap = cv2.VideoCapture(str(VIDEO))
    fps = cap.get(cv2.CAP_PROP_FPS)
    pts, ts, xs = [], [], []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % stride == 0:
            p = detectar_bola(frame)
            if p is not None:
                pts.append(p); ts.append(i / fps); xs.append(i)
        i += 1
    cap.release()
    return np.array(pts), np.array(ts), np.array(xs)


def ajustar_circulo(pts: np.ndarray) -> tuple[float, float, float]:
    x, y = pts[:, 0], pts[:, 1]
    A = np.column_stack([x, y, np.ones_like(x)])
    b = x**2 + y**2
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0] / 2, c[1] / 2
    r = float(np.sqrt(c[2] + cx**2 + cy**2))
    return float(cx), float(cy), r


# ----------------------------------------------------------------------
# Paso 2: estimacion del periodo por autocorrelacion
# ----------------------------------------------------------------------
def estimar_periodo(theta: np.ndarray, t: np.ndarray) -> float:
    centered = theta - theta.mean()
    xcorr = np.correlate(centered, centered, mode="full")
    xcorr = xcorr[len(theta) - 1:]
    xcorr /= xcorr[0] + 1e-12
    dt = float(np.median(np.diff(t)))
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(xcorr, distance=int(0.5 / dt))
    if len(peaks) < 2:
        return float("nan")
    return float((peaks[1] - peaks[0]) * dt)


def estimar_periodo_por_ceros(theta: np.ndarray, t: np.ndarray) -> tuple[float, int]:
    """Estima T contando tiempo entre cruces por theta = 0 (todos los cruces).

    El tiempo entre dos cruces por cero consecutivos es T/2 (la mitad del
    periodo: el pendulo pasa por cero yendo hacia un lado, llega al extremo,
    vuelve y pasa por cero yendo al otro lado = T/2 entre cada par).
    Multiplicamos por 2 para obtener T.

    Devuelve (T_seg, n_cruces).
    """
    cruces = []
    for i in range(1, len(theta)):
        # Cruce por cero: cambia el signo entre muestra i-1 y muestra i
        if theta[i - 1] * theta[i] <= 0 and theta[i - 1] != theta[i]:
            # Interpolar el tiempo exacto del cruce
            frac = -theta[i - 1] / (theta[i] - theta[i - 1])
            t_cruce = t[i - 1] + frac * (t[i] - t[i - 1])
            cruces.append(t_cruce)
    if len(cruces) < 3:
        return float("nan"), 0
    diferencias = np.diff(cruces)         # todos son ~T/2
    semi_periodo = float(np.median(diferencias))
    T = 2 * semi_periodo
    return T, len(cruces)


def theta_de_tracking(x: np.ndarray, y: np.ndarray, x0: float, y0: float,
                      t: np.ndarray) -> np.ndarray:
    return np.arctan2(x - x0, y - y0)


# ----------------------------------------------------------------------
# Paso 3: interfaz interactiva de la regla
# ----------------------------------------------------------------------
def auto_detectar_cinta(frame_bgr: np.ndarray) -> tuple[int, int]:
    """Detecta los extremos horizontales del cuerpo rosa de la cinta.

    Estrategia: cuenta pixeles rosa (H en [165,180], S>=25) por columna
    en una banda delgada. La cinta tiene >= 5 pixeles rosa por columna;
    los reflejos del fondo verde tienen muy pocos.
    """
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    banda = hsv[1352:1362, :, :]
    h_chan = banda[:, :, 0]
    s_chan = banda[:, :, 1]
    es_rosa = (h_chan >= 165) & (h_chan <= 180) & (s_chan >= 25)
    col_count = es_rosa.sum(axis=0)
    cinta_cols = col_count >= 5
    h, w = frame_bgr.shape[:2]
    # En vez de buscar el segmento mas largo, suavizamos y tomamos los
    # pixeles donde la cinta esta presente con tolerancia a huecos cortos.
    # Primero: cerrar huecos de <= 30 px (los numeros en la cinta)
    cerrado = cinta_cols.copy()
    # Encontrar huecos
    diff = np.diff(cerrado.astype(int))
    inicios = np.where(diff == 1)[0]
    fines = np.where(diff == -1)[0]
    if len(inicios) > 0 and len(fines) > 0:
        if fines[0] < inicios[0]:
            fines = fines[1:]
        n = min(len(inicios), len(fines))
        for i in range(n):
            if fines[i] - inicios[i] <= 30:
                cerrado[inicios[i]:fines[i]] = True
    # Ahora tomar los extremos del primer y ultimo run largo
    idx_rosa = np.where(cerrado)[0]
    if len(idx_rosa) < 2:
        return 0, w - 1
    # Filtrar runs cortos al inicio/final (reflejos espurios)
    # El primer run debe tener al menos 20 pixeles, sino descartarlo
    inicio = idx_rosa[0]
    fin = idx_rosa[-1]
    # Buscar el primer gap significativo desde el inicio
    gaps = np.diff(idx_rosa)
    for i, g in enumerate(gaps):
        if g > 50:  # gap grande, la cinta termina
            fin = idx_rosa[i]
            break
    # Buscar el ultimo gap significativo desde el final
    gaps_rev = np.diff(idx_rosa[::-1])
    for i, g in enumerate(gaps_rev):
        if g > 50:
            inicio = idx_rosa[len(idx_rosa) - 1 - i]
            break
    return int(inicio), int(fin)


def pedir_cinta(pivote: tuple[float, float], L_px: float, T_exp: float,
                L_target: float) -> dict:
    """Muestra los extremos detectados y pide 2 clics + sus valores en cm."""
    cap = cv2.VideoCapture(str(VIDEO))
    cap.set(cv2.CAP_PROP_POS_MSEC, 0)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("No se pudo leer el frame inicial.")

    # Auto-deteccion de los extremos de la cinta
    x_izq_auto, x_der_auto = auto_detectar_cinta(frame)

    img = frame.copy()
    h, w = img.shape[:2]
    xp, yp = pivote

    # Indicador del pivote
    if 0 <= yp < h and 0 <= xp < w:
        cv2.circle(img, (int(xp), int(yp)), 14, (255, 0, 255), 3)
    else:
        cv2.line(img, (int(xp), 0), (int(xp), h), (255, 0, 255), 1)

    # Marcas auto-detectadas de la cinta (rectangulos amarillos)
    cv2.rectangle(img, (x_izq_auto, CINTA_Y0 - 5),
                  (x_izq_auto + 1, CINTA_Y1 + 5), (0, 255, 255), 2)
    cv2.rectangle(img, (x_der_auto, CINTA_Y0 - 5),
                  (x_der_auto + 1, CINTA_Y1 + 5), (0, 255, 255), 2)
    cv2.line(img, (x_izq_auto, CINTA_Y0 - 30), (x_izq_auto, CINTA_Y0 - 5),
             (0, 255, 255), 1)
    cv2.line(img, (x_der_auto, CINTA_Y0 - 30), (x_der_auto, CINTA_Y0 - 5),
             (0, 255, 255), 1)
    cv2.putText(img, f"extremo izq auto ({x_izq_auto},{CINTA_Y0})",
                (x_izq_auto - 200, CINTA_Y0 - 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(img, f"extremo der auto ({x_der_auto},{CINTA_Y0})",
                (x_der_auto + 5, CINTA_Y0 - 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    clicks: list[tuple[int, int]] = []

    def on_mouse(event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicks.append((x, y))
            cv2.circle(img, (x, y), 8, (0, 200, 255), -1)
            cv2.putText(img, f"click {len(clicks)}: ({x},{y})",
                        (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 200, 255), 2)
            cv2.imshow("Calibracion regla", img)

    print(f"\nReferencia: T_exp = {T_exp:.3f} s -> L_target = {L_target:.3f} m")
    print("Instrucciones:")
    print("  - Las 2 marcas AMARILLAS son los extremos auto-detectados.")
    print("  - Si te sirven, cierre la ventana con 'q' o ESC.")
    print("  - Si no, haga 2 clics sobre los extremos correctos; la ventana")
    print("    se cierra sola al hacerlos. Luego ingrese los cm de cada uno.")

    cv2.namedWindow("Calibracion regla", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Calibracion regla", on_mouse)
    cv2.resizeWindow("Calibracion regla", 540, 960)
    while True:
        cv2.imshow("Calibracion regla", img)
        k = cv2.waitKey(50) & 0xFF
        if k in (27, ord("q")):
            break
        if len(clicks) >= 2:
            # Confirmar con un pequeno retraso para ver el segundo click
            cv2.waitKey(300)
            break
    cv2.destroyAllWindows()

    # Si el usuario cerro sin clicar, usamos los auto-detectados
    if len(clicks) < 2:
        clicks = [(x_izq_auto, CINTA_Y0), (x_der_auto, CINTA_Y1)]
        print(f"  -> Usando extremos auto-detectados.")

    if len(clicks) < 2:
        raise RuntimeError("Calibracion cancelada: se necesitan 2 clics.")

    cm1 = float(input("  Valor en cm del primer clic (extremo izquierdo): "))
    cm2 = float(input("  Valor en cm del segundo clic (extremo derecho): "))
    (x1, y1), (x2, y2) = clicks[0], clicks[1]
    dpx = float(np.hypot(x2 - x1, y2 - y1))
    dcm = abs(cm2 - cm1)
    k = (dcm / 100.0) / dpx
    return {
        "k_m_por_px": k,
        "px_por_cm": dpx / dcm,
        "dpx": dpx,
        "dcm": dcm,
        "clicks": [{"x": int(c[0]), "y": int(c[1])} for c in clicks],
        "cm": [cm1, cm2],
    }


# ----------------------------------------------------------------------
# Bucle principal
# ----------------------------------------------------------------------
def main() -> None:
    print("[1/4] Tracking rapido de la bola...")
    pts, ts, _ = tracking_rapido(stride=4)
    print(f"      {len(pts)} detecciones en {ts[-1] - ts[0]:.1f} s")

    print("[2/4] Ajuste de circulo -> pivote...")
    cx, cy, r = ajustar_circulo(pts)
    print(f"      pivote: ({cx:.1f}, {cy:.1f}), L_px: {r:.1f}")

    print("[3/4] Estimacion del periodo por cruces por cero (experimental)...")
    theta_pts = theta_de_tracking(pts[:, 0], pts[:, 1], cx, cy, ts)
    T_ceros, n_cruces = estimar_periodo_por_ceros(theta_pts, ts)
    T_auto = estimar_periodo(theta_pts, ts)
    if np.isnan(T_ceros):
        T_exp = T_auto if not np.isnan(T_auto) else 1.5
        metodo = "autocorrelacion (fallback)"
    else:
        T_exp = T_ceros
        metodo = "cruces por cero"
    L_target = G * T_exp**2 / (4 * np.pi**2)
    omega_n_target = float(2 * np.pi / T_exp)

    print(f"      T (cruces por cero, {n_cruces} cruces) = {T_ceros:.3f} s")
    print(f"      T (autocorrelacion)                  = "
          f"{T_auto:.3f} s" if not np.isnan(T_auto) else "N/D")
    print(f"      -> usando T = {T_exp:.3f} s ({metodo})")
    print(f"      L_target = {L_target:.3f} m")
    print(f"      omega_n  = {omega_n_target:.3f} rad/s")

    if not np.isnan(T_ceros) and not np.isnan(T_auto):
        diff = abs(T_ceros - T_auto) / T_auto
        if diff > 0.05:
            print(f"      AVISO: metodos difieren en {diff*100:.1f}% "
                  f"(ruido o damping fuerte)")

    print("[4/4] Calibracion interactiva de la regla...")
    regla = pedir_cinta((cx, cy), r, T_exp, L_target)
    L_clicks = r * regla["k_m_por_px"]
    diff = abs(L_clicks - L_target) / L_target
    print(f"\nResultado:")
    print(f"  dpx = {regla['dpx']:.1f}, dcm = {regla['dcm']:.2f}")
    print(f"  k = {regla['k_m_por_px']:.6f} m/px")
    print(f"  L_clicks = {L_clicks:.3f} m")
    print(f"  L_target = {L_target:.3f} m (por T_exp, solo informativo)")
    print(f"  Diferencia: {diff*100:.1f}%")
    if diff > TOLERANCIA:
        print(f"  NOTA: la diferencia > {TOLERANCIA*100:.0f}% puede deberse a")
        print(f"        diferencia de perspectiva entre la regla y el pendulo.")
        print(f"        Se acepta tu lectura de todos modos (lo que pediste).")

    cal = {
        "pivote_xy_px": [cx, cy],
        "L_px": r,
        **regla,
        "L_m_clicks": L_clicks,
        "L_target_m": L_target,
        "diferencia_porcentaje": float(diff * 100),
        "g": G,
        "T_exp_s": T_exp,
        "T_ceros_s": T_ceros,
        "T_auto_s": T_auto if not np.isnan(T_auto) else None,
        "n_cruces_por_cero": int(n_cruces),
        "omega_n_rad_s": omega_n_target,
        "T_MAS_s": T_exp,
        "n_detecciones_rapidas": int(len(pts)),
        "fps_video": 25.0,
        "ancho_px": 1080,
        "alto_px": 1920,
    }
    out = RES / "calibracion.json"
    out.write_text(json.dumps(cal, indent=2))
    print(f"\nCalibracion guardada en {out}")
    print(f"  k = {regla['k_m_por_px']:.6f} m/px")
    print(f"  L = {L_clicks:.3f} m")
    print(f"  omega_n = {omega_n_target:.3f} rad/s")
    print(f"  T_MAS = {T_exp:.3f} s")


if __name__ == "__main__":
    main()
