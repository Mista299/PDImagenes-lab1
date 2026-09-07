"""Pipeline de seguimiento de la masa del pendulo (pasos 2-6 del PDF).

Para cada frame del video:
  2. BGR -> HSV + GaussianBlur
  3. Doble umbral inRange (rojo en H 0-10 y 170-180)
  4. Opening + Closing con kernel eliptico 5x5
  5. findContours -> contorno de mayor area -> momentos -> centroide
  6. (theta se calcula en cinematica.py)

Salida: resultados/tracking.csv con columnas t_s, x_px, y_px
"""
from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "pendulo.mp4"
RES = ROOT / "resultados"

KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))


def procesar_frame(frame_bgr: np.ndarray) -> tuple[float, float] | None:
    """Devuelve (cx, cy) del centroide de la bola, o None si falla."""
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    hsv = cv2.GaussianBlur(hsv, (5, 5), 1)

    mask = (
        cv2.inRange(hsv, np.array([0, 100, 60]), np.array([10, 255, 255]))
        | cv2.inRange(hsv, np.array([170, 100, 60]), np.array([180, 255, 255]))
    )
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL, iterations=1)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    c = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(c) < 200:
        return None
    M = cv2.moments(c)
    if M["m00"] == 0:
        return None
    return (M["m10"] / M["m00"], M["m01"] / M["m00"])


def seguir() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Procesa todos los frames. Devuelve (t, x, y) como arreglos numpy."""
    cap = cv2.VideoCapture(str(VIDEO))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ts, xs, ys = [], [], []
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        p = procesar_frame(frame)
        if p is not None:
            ts.append(i / fps)
            xs.append(p[0])
            ys.append(p[1])
        i += 1
    cap.release()
    return np.array(ts), np.array(xs), np.array(ys)


def guardar_csv(t: np.ndarray, x: np.ndarray, y: np.ndarray) -> Path:
    out = RES / "tracking.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_s", "x_px", "y_px"])
        for ti, xi, yi in zip(t, x, y):
            w.writerow([f"{ti:.4f}", f"{xi:.2f}", f"{yi:.2f}"])
    return out


def main() -> None:
    print(f"Procesando {VIDEO.name}...")
    t, x, y = seguir()
    print(f"  {len(t)} detecciones en {t[-1] - t[0]:.2f} s")
    out = guardar_csv(t, x, y)
    print(f"  Guardado en {out}")


if __name__ == "__main__":
    main()
