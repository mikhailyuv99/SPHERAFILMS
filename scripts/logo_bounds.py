"""Compute bounding box of the Sphera logo path in assets/logo.svg."""
from __future__ import annotations

import re
from pathlib import Path


def _tokenize_path(d: str) -> list[str]:
    return re.findall(r"[a-zA-Z]|-?\d*\.?\d+(?:e[-+]?\d+)?", d)


def path_bbox(d: str) -> tuple[float, float, float, float]:
    tokens = _tokenize_path(d)
    i = 0
    cmd = "M"
    cx = cy = start_x = start_y = 0.0
    xs: list[float] = []
    ys: list[float] = []

    def add(x: float, y: float) -> None:
        xs.append(x)
        ys.append(y)

    while i < len(tokens):
        t = tokens[i]
        if t.isalpha():
            cmd = t
            i += 1
            continue

        rel = cmd.islower()
        c = cmd.upper()

        if c == "M":
            x = float(tokens[i])
            y = float(tokens[i + 1])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            start_x, start_y = x, y
            add(x, y)
            i += 2
            cmd = "L" if c == "M" else "l"
        elif c == "L":
            x = float(tokens[i])
            y = float(tokens[i + 1])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            add(x, y)
            i += 2
        elif c == "C":
            for j in (0, 2, 4):
                x = float(tokens[i + j])
                y = float(tokens[i + j + 1])
                if rel:
                    x += cx
                    y += cy
                add(x, y)
            x = float(tokens[i + 4])
            y = float(tokens[i + 5])
            if rel:
                x += cx
                y += cy
            cx, cy = x, y
            i += 6
        elif c == "Z":
            cx, cy = start_x, start_y
            i += 1
        else:
            i += 1

    return min(xs), min(ys), max(xs), max(ys)


def load_path() -> str:
    svg = Path(__file__).resolve().parents[1] / "assets" / "logo.svg"
    match = re.search(r'<path d="([^"]+)"', svg.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit("path not found")
    return match.group(1)


if __name__ == "__main__":
    d = load_path()
    x0, y0, x1, y1 = path_bbox(d)
    print(f"bbox: {x0:.1f} {y0:.1f} {x1:.1f} {y1:.1f}")
    print(f"center: {(x0 + x1) / 2:.1f} {(y0 + y1) / 2:.1f}")
    print(f"span: {max(x1 - x0, y1 - y0):.1f}")
