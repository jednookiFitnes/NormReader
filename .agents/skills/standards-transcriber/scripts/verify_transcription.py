#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_transcription.py - Narzędzie audytu i walidacji przepisanych notatek normatywnych w skarbcu Obsidian.
Sprawdza spójność YAML frontmatter z bazami .base, poprawność tagów z katalogu, brak osieroconych zrzutów ekranu,
składnię tabel oraz blokuje prymitywne / automatyczne próby wektoryzacji rastrowej (auto-tracingu).
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR / "tags_catalog.json"

IMG_PATTERN = re.compile(r'!\[.*?\]\((.*?\.(?:png|jpg|jpeg|webp))\)|!\[\[(.*?\.(?:png|jpg|jpeg|webp))(?:\|.*?)?\]\]', re.IGNORECASE)
SVG_REF_PATTERN = re.compile(r'!\[.*?\]\((.*?\.svg)\)|!\[\[(.*?\.svg)(?:\|.*?)?\]\]', re.IGNORECASE)

def load_approved_tags():
    if not CATALOG_PATH.exists():
        return set()
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("flat_list", []))

def audit_svg_file(svg_path):
    """
    Weryfikuje plik SVG pod kątem składni XML oraz blokuje ślepy auto-tracing
    (wykrywając nadmierną liczbę punktów w elementach <path>, <polygon> lub <polyline>).
    """
    issues = []
    warnings = []
    if not os.path.exists(svg_path):
        return [f"Brak pliku wektorowego SVG: {svg_path}"], []

    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        if not root.tag.endswith("svg"):
            return ["Plik SVG nie posiada głównego znacznika <svg>"], []
        
        svg_text = open(svg_path, "r", encoding="utf-8").read()
        
        # Sprawdzenie czy wygenerowano tekst wektorowy (ISO / wymiary)
        has_text = "<text" in svg_text
        
        # Detekcja podejrzanie długich atrybutów d="..." (świadczy o bitmapowym auto-tracery z setkami/tysiącami segmentów)
        path_matches = re.findall(r'd="([^"]+)"', svg_text)
        for d_attr in path_matches:
            # Liczymy przybliżoną liczbę komend/węzłów w ścieżce
            nodes_count = len(re.findall(r'[MmLlHhVvCcSsQqTtAaZz]', d_attr))
            if nodes_count > 150:
                issues.append(f"KRYTYCZNE: Wykryto ścieżkę <path> z auto-tracingu o ogromnej złożoności ({nodes_count} węzłów). Zakaz auto-tracingu! Wymagane czyste CAD-SVG.")
        
        # Detekcja podejrzanie wielkich wielokątów (<polygon>)
        polygon_matches = re.findall(r'points="([^"]+)"', svg_text)
        for pts in polygon_matches:
            coords = pts.strip().split()
            if len(coords) > 100:
                issues.append(f"KRYTYCZNE: Wykryto element <polygon> z auto-tracingu ({len(coords)} punktów). Wymagane konstrukcje wektorowe CAD-SVG.")

        if not has_text and len(path_matches) > 3:
            warnings.append("Ostrzeżenie: Plik SVG nie zawiera elementów tekstowych <text> (brak oznaczeń wymiarów s_r, e lub etykiet).")

    except ET.ParseError as e:
        issues.append(f"Błąd składni XML w pliku SVG: {str(e)}")
    except Exception as e:
        issues.append(f"Błąd odczytu pliku SVG: {str(e)}")

    return issues, warnings

def verify_note(filepath, approved_tags):
    path = Path(filepath)
    issues = []
    warnings = []

    if not path.exists():
        return False, [f"Plik nie istnieje: {filepath}"], []

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Frontmatter
    fm_match = re.search(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not fm_match:
        issues.append("Brak nagłówka YAML Frontmatter (--- ... ---)")
        return False, issues, warnings

    yaml_text = fm_match.group(1)
    body = content[fm_match.end():].strip()

    # Parse simple yaml keys
    yaml_keys = set()
    for line in yaml_text.splitlines():
        k_match = re.match(r"^([a-zA-Z0-9_-]+):", line)
        if k_match:
            yaml_keys.add(k_match.group(1))

    # Detect note type
    filename_upper = path.name.upper()
    is_index = path.name.startswith("_")
    is_table = "TABLICA" in filename_upper or "norm_table" in yaml_keys
    is_drawing = "RYSUNEK" in filename_upper or "RYS." in filename_upper or "norm_drawing" in yaml_keys
    is_point = not (is_index or is_table or is_drawing)

    # 2. Check required fields
    if "index" not in yaml_keys:
        issues.append("Brak wymaganego pola 'index' w YAML")
    else:
        for line in yaml_text.splitlines():
            if "[[" in line and "]]" in line:
                if not (('"' in line) or ("'" in line)):
                    issues.append(f"Wikilink w YAML musi być ujęty w cudzysłów: {line.strip()}")

    if is_point:
        for req in ["norm_number", "norm_point", "norm_point_title", "norm_title_PL"]:
            if req not in yaml_keys:
                issues.append(f"Punkt normy wymaga pola YAML '{req}' dla widoku Normy.base")

    elif is_table:
        for req in ["norm_number", "norm_table", "norm_table_title"]:
            if req not in yaml_keys:
                issues.append(f"Tablica wymaga pola YAML '{req}' dla widoku Normy.base")

    elif is_drawing:
        for req in ["norm_number", "norm_drawing", "norm_drawing_title"]:
            if req not in yaml_keys:
                issues.append(f"Rysunek wymaga pola YAML '{req}' dla widoku Normy.base")

    # 3. Check tags (Unicode support)
    note_tags = set()
    tags_match = re.search(r"tags:\r?\n(.*?)(?=\r?\n[a-zA-Z0-9_-]+:|\Z)", yaml_text, re.DOTALL)
    if tags_match:
        for line in tags_match.group(1).splitlines():
            clean = line.strip().lstrip("-").strip().strip('"').strip("'").lstrip("#")
            if clean and not clean.startswith("[["):
                note_tags.add(clean)

    body_no_code = re.sub(r"```.*?```|`[^`]*`", "", body, flags=re.DOTALL)
    for m in re.finditer(r"(?<!\S)#([\w\-\/]+)", body_no_code, re.UNICODE):
        t = m.group(1)
        if not t.isdigit() and not re.fullmatch(r"[0-9a-fA-F]{3,8}", t):
            note_tags.add(t)

    if approved_tags:
        for t in note_tags:
            if t not in approved_tags:
                warnings.append(f"Nieznany tag (brak w tags_catalog.json): #{t} - wymaga akceptacji użytkownika")

    # 4. Check for remaining unreplaced screenshots
    unreplaced_images = []
    for m in IMG_PATTERN.finditer(body):
        img_name = m.group(1) or m.group(2)
        if not img_name.lower().endswith(".svg"):
            unreplaced_images.append(img_name)

    if unreplaced_images:
        warnings.append(f"W treści notatki nadal znajdują się zrzuty ekranu ({len(unreplaced_images)}): {', '.join(unreplaced_images)}")

    # 5. Audit referenced SVG files for auto-tracing artifacts
    note_dir = path.parent
    for m in SVG_REF_PATTERN.finditer(body):
        svg_name = m.group(1) or m.group(2)
        if svg_name:
            # Sprawdź lokalizację w folderze normy lub Attachments/
            possible_paths = [
                note_dir / svg_name,
                note_dir / "Attachments" / Path(svg_name).name,
                note_dir.parent / "Attachments" / Path(svg_name).name
            ]
            found_svg = None
            for p in possible_paths:
                if p.exists():
                    found_svg = p
                    break
            
            if found_svg:
                svg_issues, svg_warnings = audit_svg_file(found_svg)
                issues.extend([f"[{svg_name}] {iss}" for iss in svg_issues])
                warnings.extend([f"[{svg_name}] {w}" for w in svg_warnings])

    # 6. Table validation
    if is_table:
        has_md_table = bool(re.search(r'\|.*?\|.*?\|\r?\n\|(?:\s*[:-]+[-| :]*)\|\r?\n\|.*?\|', body))
        has_html_table = "<table" in body.lower()
        if not (has_md_table or has_html_table):
            warnings.append("Notatka tablicy nie zawiera wykrytej tabeli Markdown ani HTML <table>")

    return (len(issues) == 0), issues, warnings

def main():
    parser = argparse.ArgumentParser(description="Weryfikacja integralności przepisanej notatki Obsidian oraz blokada auto-tracingu SVG")
    parser.add_argument("--file", "-f", required=True, help="Ścieżka do pliku .md do weryfikacji")
    args = parser.parse_args()

    approved_tags = load_approved_tags()
    valid, issues, warnings = verify_note(args.file, approved_tags)

    print(f"\n=======================================================")
    print(f"🔍 AUDYT NOTATKI ORAZ GRAFIK CAD-SVG: {Path(args.file).name}")
    print(f"=======================================================")
    if valid and not warnings:
        print("[SUKCES] Notatka jest w 100% poprawna, spełnia wymogi Normy.base i nie zawiera wykrytych śladów auto-tracingu.")
    else:
        if issues:
            print(f"[BŁĘDY KRYTYCZNE] ({len(issues)}):")
            for iss in issues:
                print(f"  ❌ {iss}")
        if warnings:
            print(f"[OSTRZEŻENIA / UWAGI] ({len(warnings)}):")
            for w in warnings:
                print(f"  ⚠️ {w}")
    print(f"=======================================================\n")

    sys.exit(0 if valid else 1)

if __name__ == "__main__":
    main()