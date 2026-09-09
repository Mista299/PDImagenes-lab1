"""Exporta un video anotado del pendulo.

Dibuja: estela de la trayectoria, linea pivote-masa, linea vertical de
referencia (theta=0), y un panel con t, theta, omega, alpha y FPS en vivo.
Salida: resultados/video_anotado.mp4
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "pendulo.mp4"
RES = ROOT / "resultados"
OUT = RES / "video_anotado.mp4"

TRAIL_COLOR = (0, 140, 255)
ROD_COLOR = (0, 0, 255)
REF_COLOR = (255, 255, 0)
MASS_COLOR = (0, 0, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _linea_vertical_punteada(img: np.ndarray, x: int, color: tuple[int, int, int]) -> None:
    h = img.shape[0]
    y = 0
    while y < h:
        y2 = min(y + 15, h - 1)
        cv2.line(img, (x, y), (x, y2), color, 2, cv2.LINE_AA)
        y += 28


def _panel_texto(img: np.ndarray, lineas: list[str]) -> None:
    escala = 0.65
    grosor = 2
    alto_linea = 0
    ancho_max = 0
    for linea in lineas:
        (tw, th), _ = cv2.getTextSize(linea, FONT, escala, grosor)
        ancho_max = max(ancho_max, tw)
        alto_linea = max(alto_linea, th)

    margen = 10
    x0 = margen
    y0 = margen
    ancho = ancho_max + 2 * margen
    alto = len(lineas) * (alto_linea + 8) + 2 * margen
    cv2.rectangle(img, (x0, y0), (x0 + ancho, y0 + alto), (0, 0, 0), -1)

    for i, linea in enumerate(lineas):
        y = y0 + margen + (i + 1) * (alto_linea + 8)
        cv2.putText(img, linea, (x0 + margen, y), FONT, escala, (255, 255, 255), grosor, cv2.LINE_AA)


def exportar(entrada: Path | str = VIDEO, salida: Path | str = OUT) -> Path:
    cal = json.loads((RES / "calibracion.json").read_text())
    xp, yp = cal["pivote_xy_px"]

    track = pd.read_csv(RES / "tracking.csv")
    cine = pd.read_csv(RES / "cinematica.csv")

    t_track = track["t_s"].to_numpy()
    x_track = track["x_px"].to_numpy()
    y_track = track["y_px"].to_numpy()

    t_cine = cine["t_s"].to_numpy()
    theta = cine["theta_rad"].to_numpy()
    omega = cine["omega_rad_s"].to_numpy()
    alpha = cine["alpha_rad_s2"].to_numpy()

    cap = cv2.VideoCapture(str(entrada))
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir {entrada}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(salida), fourcc, fps, (ancho, alto))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError("No se pudo crear el video de salida (codec mp4v no disponible)")

    trail: list[tuple[int, int]] = []
    prev = time.perf_counter()
    i = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        t = i / fps
        i += 1

        x = float(np.interp(t, t_track, x_track))
        y = float(np.interp(t, t_track, y_track))
        th = float(np.interp(t, t_cine, theta))
        w = float(np.interp(t, t_cine, omega))
        a = float(np.interp(t, t_cine, alpha))

        trail.append((int(x), int(y)))

        ahora = time.perf_counter()
        dt = ahora - prev
        prev = ahora
        fps_vivo = 1.0 / dt if dt > 0 else 0.0

        pts = np.array(trail, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], False, TRAIL_COLOR, 2, cv2.LINE_AA)

        cv2.line(frame, (int(xp), int(yp)), (int(x), int(y)), ROD_COLOR, 2, cv2.LINE_AA)
        cv2.circle(frame, (int(x), int(y)), 10, MASS_COLOR, -1, cv2.LINE_AA)
        _linea_vertical_punteada(frame, int(xp), REF_COLOR)

        lineas = [
            f"t = {t:.3f} s",
            f"theta = {np.degrees(th):.2f} deg ({th:.4f} rad)",
            f"omega = {w:.4f} rad/s",
            f"alpha = {a:.4f} rad/s^2",
            f"FPS = {fps_vivo:.1f}",
        ]
        _panel_texto(frame, lineas)

        writer.write(frame)

    cap.release()
    writer.release()
    return Path(salida)


def main() -> None:
    out = exportar()
    print(f"Video anotado guardado en {out}")


if __name__ == "__main__":
    main()
