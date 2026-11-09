#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_table_to_svg.py — Deterministyczna kompilacja tabel HTML do wektora SVG dla norm technicznych.
Gwarantuje Single-Page SVG Invariant (Pages == 1, brak <pageSet>/<page>), co zapobiega pustym polom w Obsidianie.

Użycie:
    python render_table_to_svg.py --html "tabela.html" --out-svg "Attachments/Tablica_4.svg" [--out-png "Attachments/Tablica_4.png"] [--width 190mm] [--height 210mm] [--auto-height]
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile

def find_edge_binary():
    candidates = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Users\%USERNAME%\AppData\Local\Microsoft\Edge\Application\msedge.exe'
    ]
    for c in candidates:
        expanded = os.path.expandvars(c)
        if os.path.exists(expanded):
            return expanded
    return 'msedge'

def get_pdf_page_count(pdf_path):
    info_res = subprocess.run(['pdfinfo', pdf_path], capture_output=True, text=True)
    if info_res.returncode == 0:
        for line in info_res.stdout.splitlines():
            if line.startswith('Pages:'):
                return int(line.split(':')[1].strip())
    return 1

def build_full_html(html_content, page_width, page_height, margin):
    # Strip any existing @page from html_content to avoid conflicts
    clean_body = re.sub(r'@page\s*\{[^}]*\}', '', html_content)
    
    if '<html' not in clean_body.lower():
        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
  size: {page_width} {page_height};
  margin: {margin};
}}
* {{
  box-sizing: border-box;
}}
html, body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #ffffff;
  color: #111111;
  margin: 0;
  padding: 0;
  width: 100%;
}}
</style>
</head>
<body>
{clean_body}
</body>
</html>"""
    else:
        full_html = clean_body
    return full_html

def render_html_to_svg(html_path, out_svg, out_png=None, out_pdf=None, page_width='190mm', page_height='210mm', margin='3mm', auto_height=True):
    edge_bin = find_edge_binary()
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract numerical height if in mm
    h_match = re.search(r'(\d+)\s*mm', page_height)
    curr_h_mm = int(h_match.group(1)) if h_match else 210

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_html = os.path.join(tmpdir, 'render_table.html')
        tmp_pdf = os.path.join(tmpdir, 'render_table.pdf')
        
        # 1. Edge headless: HTML -> PDF with Single-Page verification loop
        while True:
            full_html = build_full_html(html_content, page_width, f"{curr_h_mm}mm", margin)
            with open(tmp_html, 'w', encoding='utf-8') as f:
                f.write(full_html)
                
            cmd_edge = [
                edge_bin,
                '--headless',
                '--no-pdf-header-footer',
                f'--print-to-pdf={tmp_pdf}',
                tmp_html
            ]
            res_edge = subprocess.run(cmd_edge, capture_output=True, text=True)
            if not os.path.exists(tmp_pdf) or os.path.getsize(tmp_pdf) == 0:
                print(f"[BŁĄD] Edge headless nie wygenerował pliku PDF: {res_edge.stderr}", file=sys.stderr)
                sys.exit(1)

            pages = get_pdf_page_count(tmp_pdf)
            if pages == 1 or not auto_height:
                break
            
            # Table exceeded height and split into multiple pages -> increase height
            curr_h_mm += 15
            if curr_h_mm > 800:  # safety ceiling
                break

        # 2. pdftocairo: PDF -> SVG
        os.makedirs(os.path.dirname(os.path.abspath(out_svg)), exist_ok=True)
        cmd_svg = ['pdftocairo', '-svg', tmp_pdf, out_svg]
        res_svg = subprocess.run(cmd_svg, capture_output=True, text=True)
        if res_svg.returncode != 0 or not os.path.exists(out_svg):
            print(f"[BŁĄD] pdftocairo nie zdołał wygenerować SVG: {res_svg.stderr}", file=sys.stderr)
            sys.exit(1)
            
        # Verify Single-Page SVG Invariant (no <pageSet>)
        with open(out_svg, 'r', encoding='utf-8') as f:
            svg_data = f.read()
        if '<pageSet>' in svg_data:
            print(f"[OSTRZEŻENIE] SVG zawiera <pageSet>! Zwiększ wysokość strony, aby uniknąć pustych pól w Obsidianie.", file=sys.stderr)
        else:
            print(f"[SUKCES] Wygenerowano czysty 1-stronicowy SVG: {out_svg} ({os.path.getsize(out_svg)} B, h={curr_h_mm}mm)")
        
        # 3. Opcjonalnie pdftocairo: PDF -> PNG (300 DPI)
        if out_png:
            os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
            png_base = os.path.splitext(out_png)[0]
            cmd_png = ['pdftocairo', '-png', '-r', '300', tmp_pdf, png_base]
            subprocess.run(cmd_png, capture_output=True, text=True)
            gen_png = png_base + '-1.png'
            if os.path.exists(gen_png):
                if os.path.exists(out_png) and os.path.abspath(out_png) != os.path.abspath(gen_png):
                    os.remove(out_png)
                os.replace(gen_png, out_png)
                print(f"[SUKCES] Wygenerowano High-DPI PNG: {out_png} ({os.path.getsize(out_png)} B)")
                
        # 4. Opcjonalnie zachowanie PDF
        if out_pdf:
            os.makedirs(os.path.dirname(os.path.abspath(out_pdf)), exist_ok=True)
            import shutil
            shutil.copy2(tmp_pdf, out_pdf)
            print(f"[SUKCES] Zapisano wektorowy PDF: {out_pdf} ({os.path.getsize(out_pdf)} B)")

def main():
    parser = argparse.ArgumentParser(description="Kompilacja tabel HTML do wektorowego SVG/PDF/PNG z gwarancją 1 strony.")
    parser.add_argument('--html', required=True, help="Ścieżka do pliku HTML lub fragmentu tabeli.")
    parser.add_argument('--out-svg', required=True, help="Docelowa ścieżka do pliku SVG.")
    parser.add_argument('--out-png', help="Opcjonalna ścieżka do pliku High-DPI PNG.")
    parser.add_argument('--out-pdf', help="Opcjonalna ścieżka do pliku PDF.")
    parser.add_argument('--width', default='190mm', help="Szerokość strony (domyślnie 190mm).")
    parser.add_argument('--height', default='210mm', help="Wysokość strony (domyślnie 210mm).")
    parser.add_argument('--margin', default='3mm', help="Margines strony (domyślnie 3mm).")
    parser.add_argument('--no-auto-height', dest='auto_height', action='store_false', help="Wyłącza automatyczne dopasowywanie wysokości do 1 strony.")
    parser.set_defaults(auto_height=True)
    
    args = parser.parse_args()
    render_html_to_svg(
        html_path=args.html,
        out_svg=args.out_svg,
        out_png=args.out_png,
        out_pdf=args.out_pdf,
        page_width=args.width,
        page_height=args.height,
        margin=args.margin,
        auto_height=args.auto_height
    )

if __name__ == '__main__':
    main()
