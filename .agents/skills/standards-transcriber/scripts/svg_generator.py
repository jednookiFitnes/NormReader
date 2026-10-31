#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg_generator.py - Moduł CAD-SVG i CLI do tworzenia oraz walidacji rysunków technicznych w normach.
Obsługuje linie wymiarowe ISO, indeksy dolne (np. s_r), szrafurę techniczną (<pattern>),
gładkie ścieżki Béziera oraz czyszczenie znaków wodnych z wycinków rastrowych.
"""

import sys
import os
import math
import re
import argparse
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def format_math_subscripts(text: str) -> str:
    """
    Zamienia zapis 's_r' lub 'PFH_D' na czysty tekst SVG z indeksem dolnym <tspan>.
    Bezpiecznie escapuje znaki XML (<, >, &).
    """
    parts = re.split(r'([A-Za-z0-9]+_[A-Za-z0-9]+)', text)
    out = []
    for part in parts:
        if "_" in part and not part.startswith("_") and not part.endswith("_"):
            base, sub = part.split("_", 1)
            out.append(
                f'{escape(base)}<tspan dy="0.3em" font-size="75%" font-style="normal">{escape(sub)}</tspan>'
                f'<tspan dy="-0.3em" font-size="100%">&#8203;</tspan>'
            )
        else:
            out.append(escape(part))
    return "".join(out)


class TechnicalSVG:
    def __init__(self, width=500, height=400, title="Rysunek Techniczny"):
        self.width = width
        self.height = height
        self.title = title
        self.elements = []
        self.defs = [
            # Ostry grot strzałki wymiarowej wg ISO 129 (końcowy)
            '''<marker id="arrow" viewBox="0 0 12 6" refX="11.5" refY="3" markerWidth="8" markerHeight="6" orient="auto">
                <path d="M 0 0.5 L 12 3 L 0 5.5 z" fill="#111111"/>
            </marker>''',
            # Ostry grot strzałki wymiarowej wg ISO 129 (początkowy)
            '''<marker id="arrow-start" viewBox="0 0 12 6" refX="0.5" refY="3" markerWidth="8" markerHeight="6" orient="auto">
                <path d="M 12 0.5 L 0 3 L 12 5.5 z" fill="#111111"/>
            </marker>''',
            # Szrafura techniczna 45 stopni (kreskowanie stref i przekrojów)
            '''<pattern id="hatch-45" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="12" stroke="#222222" stroke-width="1.4"/>
            </pattern>''',
            # Szrafura techniczna -45 (135) stopni
            '''<pattern id="hatch-135" width="12" height="12" patternTransform="rotate(135 0 0)" patternUnits="userSpaceOnUse">
                <line x1="0" y1="0" x2="0" y2="12" stroke="#222222" stroke-width="1.4"/>
            </pattern>'''
        ]

    def add_rect(self, x, y, width, height, rx=0, ry=0, fill="#ffffff", stroke="#111111", stroke_width=1.6, stroke_dash=None):
        dash_attr = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def add_hatch_zone(self, x, y, width, height, angle=45, border=False):
        """Dodaje strefę kreskowaną (szrafurę), która nie zlewa się z elementami na wierzchu."""
        pat = "url(#hatch-45)" if angle == 45 else "url(#hatch-135)"
        stroke = "#111111" if border else "none"
        sw = 1.4 if border else 0
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{pat}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def add_path(self, d, fill="none", stroke="#111111", stroke_width=2.0, stroke_linecap="round", stroke_linejoin="round", stroke_dash=None):
        """Dodaje gładką ścieżkę wektorową SVG (np. obrys dłoni, osłony, krzywą). Użyj fill='#ffffff', aby przykryć szrafurę pod spodem."""
        dash = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'stroke-linecap="{stroke_linecap}" stroke-linejoin="{stroke_linejoin}"{dash}/>'
        )

    def add_circle(self, cx, cy, r, fill="#ffffff", stroke="#111111", stroke_width=1.6):
        self.elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def add_diamond(self, cx, cy, width, height, fill="#ffffff", stroke="#111111", stroke_width=1.6):
        hw, hh = width / 2, height / 2
        points = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
        self.elements.append(
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def add_line(self, x1, y1, x2, y2, stroke="#111111", stroke_width=1.5, has_arrow=False, both_arrows=False, stroke_dash=None):
        m_start = ' marker-start="url(#arrow-start)"' if both_arrows else ""
        m_end = ' marker-end="url(#arrow)"' if (has_arrow or both_arrows) else ""
        dash = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" stroke-linecap="round"{dash}{m_start}{m_end}/>'
        )

    def add_polyline(self, points, fill="none", stroke="#111111", stroke_width=1.6, has_arrow=False, stroke_dash=None):
        pts_str = " ".join([f"{x},{y}" for x, y in points])
        marker = ' marker-end="url(#arrow)"' if has_arrow else ""
        dash = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<polyline points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash}{marker}/>'
        )

    def add_text(self, x, y, text, font_size=15, font_weight="normal", font_style="normal", text_anchor="middle", fill="#111111", rotate=0, bg_halo=False):
        lines = text.split("\n")
        transform = f' transform="rotate({rotate} {x} {y})"' if rotate != 0 else ""
        halo_attr = ' paint-order="stroke" stroke="#ffffff" stroke-width="4" stroke-linejoin="round"' if bg_halo else ""
        font_fam = "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"

        if len(lines) == 1:
            formatted = format_math_subscripts(lines[0])
            self.elements.append(
                f'<text x="{x}" y="{y}" font-family="{font_fam}" font-size="{font_size}" '
                f'font-weight="{font_weight}" font-style="{font_style}" text-anchor="{text_anchor}" '
                f'fill="{fill}" dominant-baseline="central"{halo_attr}{transform}>{formatted}</text>'
            )
        else:
            line_height = font_size * 1.3
            start_y = y - ((len(lines) - 1) * line_height / 2)
            tspans = [
                f'<tspan x="{x}" y="{start_y + i * line_height}">{format_math_subscripts(line)}</tspan>'
                for i, line in enumerate(lines)
            ]
            self.elements.append(
                f'<text font-family="{font_fam}" font-size="{font_size}" font-weight="{font_weight}" '
                f'font-style="{font_style}" text-anchor="{text_anchor}" fill="{fill}" '
                f'dominant-baseline="central"{halo_attr}{transform}>{"".join(tspans)}</text>'
            )

    def add_dimension(self, x1, y1, x2, y2, label="", text_offset=-12, font_size=16, italic=True, outside_arrows=False, ext_len=0):
        """
        Rysuje kompletną linię wymiarową ISO pomiędzy punktami (x1, y1) a (x2, y2)
        z ostrymi grotami strzałek i automatycznie obróconą etykietą (np. 's_r' lub 'e').
        """
        dx, dy = x2 - x1, y2 - y1
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        if outside_arrows:
            ux, uy = math.cos(angle_rad), math.sin(angle_rad)
            # Strzałki skierowane z zewnątrz do środka (dla małych szczelin jak wymiar 'e')
            self.add_line(x1 - ux * 22, y1 - uy * 22, x1, y1, stroke_width=1.4, has_arrow=True)
            self.add_line(x2 + ux * 22, y2 + uy * 22, x2, y2, stroke_width=1.4, has_arrow=True)
            self.add_line(x1, y1, x2, y2, stroke_width=1.2)
        else:
            self.add_line(x1, y1, x2, y2, stroke_width=1.4, both_arrows=True)

        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nx, ny = -math.sin(angle_rad), math.cos(angle_rad)
            tx, ty = mx + nx * text_offset, my + ny * text_offset
            # Utrzymuj tekst czytelny (nie do góry nogami)
            rot = angle_deg
            if rot > 90:
                rot -= 180
            elif rot < -90:
                rot += 180
            self.add_text(
                tx, ty, label,
                font_size=font_size,
                font_weight="bold",
                font_style="italic" if italic else "normal",
                rotate=rot,
                bg_halo=True
            )

    def render(self):
        defs_str = "\n    ".join(self.defs)
        elements_str = "\n    ".join(self.elements)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="100%" height="100%">
  <defs>
    {defs_str}
  </defs>
  <rect width="{self.width}" height="{self.height}" fill="#ffffff" rx="6" ry="6"/>
  <g id="diagram-content">
    {elements_str}
  </g>
</svg>
'''

    def save(self, filepath):
        svg_code = self.render()
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_code)
        return filepath


def validate_svg_file(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        if not root.tag.endswith("svg"):
            return False, "Główny znacznik nie jest znacznikiem <svg>"
        # Ostrzeżenie przed ślepym auto-tracingiem (setki punktów w polygon/path bez tekstu)
        svg_text = open(filepath, "r", encoding="utf-8").read()
        has_text = "<text" in svg_text
        huge_paths = len(re.findall(r'd="[^"]{1500,}"', svg_text))
        if huge_paths > 0 and not has_text:
            return False, "Wykryto surowe plamy z auto-tracera (brak elementów <text>, poszarpane ścieżki). Użyj konstrukcyjnego SVG!"
        return True, "Poprawny plik SVG XML"
    except Exception as e:
        return False, f"Błąd składni XML: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Generator i walidator technicznych grafik wektorowych SVG")
    parser.add_argument("--validate", "-v", help="Ścieżka do pliku SVG w celu walidacji składni XML i jakości")
    args = parser.parse_args()

    if args.validate:
        valid, msg = validate_svg_file(args.validate)
        if valid:
            print(f"[OK] {msg}: {args.validate}")
            sys.exit(0)
        else:
            print(f"[BLAD] {msg}: {args.validate}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Użyj jako moduł Python (from svg_generator import TechnicalSVG) lub przetestuj z flagą --validate <plik.svg>")


if __name__ == "__main__":
    main()