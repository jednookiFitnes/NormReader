#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg_generator.py - Moduł i CLI do tworzenia oraz walidacji czystych technicznych grafik wektorowych SVG.
Zgodny z Obsidianem (zarówno tryb ciemny, jak i jasny), standardem UTF-8 i polskimi znakami diakrytycznymi.
"""

import sys
import os
import argparse
import xml.etree.ElementTree as ET

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

class TechnicalSVG:
    def __init__(self, width=800, height=600, title="Rysunek Techniczny"):
        self.width = width
        self.height = height
        self.title = title
        self.elements = []
        self.defs = [
            # Standardowy grot strzałki inżynierskiej
            '''<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#222222"/>
            </marker>''',
            # Grot strzałki odwróconej
            '''<marker id="arrow-start" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 10 1 L 0 5 L 10 9 z" fill="#222222"/>
            </marker>'''
        ]

    def add_rect(self, x, y, width, height, rx=4, ry=4, fill="#fdfdfd", stroke="#222222", stroke_width=1.5, stroke_dash=None):
        dash_attr = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" ry="{ry}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def add_diamond(self, cx, cy, width, height, fill="#ffffff", stroke="#222222", stroke_width=1.5):
        hw = width / 2
        hh = height / 2
        points = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
        self.elements.append(
            f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )

    def add_line(self, x1, y1, x2, y2, stroke="#222222", stroke_width=1.5, has_arrow=False, stroke_dash=None):
        marker = ' marker-end="url(#arrow)"' if has_arrow else ""
        dash = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{stroke_width}"{dash}{marker}/>'
        )

    def add_polyline(self, points, stroke="#222222", stroke_width=1.5, has_arrow=False, stroke_dash=None):
        pts_str = " ".join([f"{x},{y}" for x, y in points])
        marker = ' marker-end="url(#arrow)"' if has_arrow else ""
        dash = f' stroke-dasharray="{stroke_dash}"' if stroke_dash else ""
        self.elements.append(
            f'<polyline points="{pts_str}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}"{dash}{marker}/>'
        )

    def add_text(self, x, y, text, font_size=13, font_weight="normal", text_anchor="middle", fill="#111111"):
        # Obsługa wieloliniowego tekstu
        lines = text.split("\n")
        if len(lines) == 1:
            self.elements.append(
                f'<text x="{x}" y="{y}" font-family="system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" '
                f'font-size="{font_size}" font-weight="{font_weight}" text-anchor="{text_anchor}" fill="{fill}" '
                f'dominant-baseline="central">{lines[0]}</text>'
            )
        else:
            line_height = font_size * 1.3
            total_h = (len(lines) - 1) * line_height
            start_y = y - (total_h / 2)
            tspan_elements = []
            for i, line in enumerate(lines):
                cur_y = start_y + (i * line_height)
                tspan_elements.append(f'<tspan x="{x}" y="{cur_y}">{line}</tspan>')
            self.elements.append(
                f'<text font-family="system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" '
                f'font-size="{font_size}" font-weight="{font_weight}" text-anchor="{text_anchor}" fill="{fill}" '
                f'dominant-baseline="central">{"".join(tspan_elements)}</text>'
            )

    def render(self):
        defs_str = "\n    ".join(self.defs)
        elements_str = "\n    ".join(self.elements)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="100%" height="100%">
  <defs>
    {defs_str}
  </defs>
  <!-- Tło o wysokiej czytelności -->
  <rect width="{self.width}" height="{self.height}" fill="#ffffff" rx="6" ry="6"/>
  
  <!-- Elementy grafiki technicznej -->
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
        return True, "Poprawny plik SVG XML"
    except Exception as e:
        return False, f"Błąd składni XML: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Generator i walidator technicznych grafik wektorowych SVG")
    parser.add_argument("--validate", "-v", help="Ścieżka do pliku SVG w celu walidacji składni XML")
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
        print("Użyj jako moduł Python (from svg_generator import TechnicalSVG) lub przetestuj za pomocą flagi --validate <plik.svg>")

if __name__ == "__main__":
    main()
