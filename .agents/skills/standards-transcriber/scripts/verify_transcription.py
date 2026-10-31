#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_transcription.py - Narzędzie audytu i walidacji przepisanych notatek normatywnych w skarbcu Obsidian.
Sprawdza spójność YAML frontmatter z bazami .base, poprawność tagów z katalogu, brak osieroconych zrzutów ekranu oraz składnię tabel.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
CATALOG_PATH = SCRIPT_DIR / "tags_catalog.json"

IMG_PATTERN = re.compile(r'!\[.*?\]\((.*?\.(?:png|jpg|jpeg|webp))\)|!\[\[(.*?\.(?:png|jpg|jpeg|webp))(?:\|.*?)?\]\]', re.IGNORECASE)

def load_approved_tags():
    if not CATALOG_PATH.exists():
        return set()
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("flat_list", []))

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
        # Check if wikilinks in index are quoted
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

    # 3. Check tags
    note_tags = set()
    # Frontmatter tags
    tags_match = re.search(r"tags:\r?\n(.*?)(?=\r?\n[a-zA-Z0-9_-]+:|\Z)", yaml_text, re.DOTALL)
    if tags_match:
        for line in tags_match.group(1).splitlines():
            clean = line.strip().lstrip("-").strip().strip('"').strip("'").lstrip("#")
            if clean and not clean.startswith("[["):
                note_tags.add(clean)

    # Inline tags
    for m in re.finditer(r"(?<!\S)#([a-zA-Z0-9_\-\/]+)", body):
        t = m.group(1)
        if not t.isdigit():
            note_tags.add(t)

    if approved_tags:
        for t in note_tags:
            if t not in approved_tags:
                warnings.append(f"Nieznany tag (brak w tags_catalog.json): #{t} - wymaga akceptacji użytkownika")

    # 4. Check for remaining unreplaced screenshots
    unreplaced_images = []
    for m in IMG_PATTERN.finditer(body):
        img_name = m.group(1) or m.group(2)
        # Ignoruj ewentualne piktogramy wektorowe .svg
        if not img_name.lower().endswith(".svg"):
            unreplaced_images.append(img_name)

    if unreplaced_images:
        warnings.append(f"W treści notatki nadal znajdują się zrzuty ekranu ({len(unreplaced_images)}): {', '.join(unreplaced_images)}")

    # 5. Table validation
    if is_table:
        has_md_table = bool(re.search(r'\|.*?\|.*?\|\r?\n\|(?:\s*[:-]+[-| :]*)\|\r?\n\|.*?\|', body))
        has_html_table = "<table" in body.lower()
        if not (has_md_table or has_html_table):
            warnings.append("Notatka tablicy nie zawiera wykrytej tabeli Markdown ani HTML <table>")

    return (len(issues) == 0), issues, warnings

def main():
    parser = argparse.ArgumentParser(description="Weryfikacja integralności przepisanej notatki Obsidian")
    parser.add_argument("--file", "-f", required=True, help="Ścieżka do pliku .md do weryfikacji")
    args = parser.parse_args()

    approved_tags = load_approved_tags()
    valid, issues, warnings = verify_note(args.file, approved_tags)

    print(f"\n=======================================================")
    print(f"🔍 AUDYT NOTATKI: {Path(args.file).name}")
    print(f"=======================================================")
    if valid and not warnings:
        print("[SUKCES] Notatka jest w 100% poprawna, spełnia wymogi Normy.base i taksonomii tagów.")
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
