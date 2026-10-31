#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_norm.py - Skaner stanu transkrypcji normy technicznej w skarbcu Obsidian.
Oszczędza kontekst LLM poprzez agregację stanu plików, zrzutów ekranu i wektorów.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

# Zapewnienie kodowania UTF-8 na Windows w standardowym wyjsciu
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_NORMY_DIR = r"G:\Mój dysk\Obsidian Vaults\Praca Vault\31 - Notes - Normy"
DEFAULT_DYREKTYWY_DIR = r"G:\Mój dysk\Obsidian Vaults\Praca Vault\32 - Notes - Dyrektywy"
DEFAULT_PRAWO_DIR = r"G:\Mój dysk\Obsidian Vaults\Praca Vault\33 - Notes - Prawo PL"

IMG_PATTERN = re.compile(r'!\[.*?\]\((.*?\.(?:png|jpg|jpeg|webp))\)|!\[\[(.*?\.(?:png|jpg|jpeg|webp))(?:\|.*?)?\]\]', re.IGNORECASE)
SVG_PATTERN = re.compile(r'!\[.*?\]\((.*?\.(?:svg))\)|!\[\[(.*?\.(?:svg))(?:\|.*?)?\]\]', re.IGNORECASE)

def find_norm_folder(search_term, root_dirs):
    for root in root_dirs:
        if not os.path.exists(root):
            continue
        # Direct folder match
        for entry in os.scandir(root):
            if entry.is_dir() and search_term.lower() in entry.name.lower():
                return Path(entry.path)
    # Check if search_term itself is an existing directory path
    p = Path(search_term)
    if p.is_dir():
        return p
    return None

def analyze_note(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Frontmatter parse
    fm_match = re.search(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    yaml_text = fm_match.group(1) if fm_match else ""
    body = content[fm_match.end():] if fm_match else content

    # Check type
    note_type = "punkt"
    if file_path.name.startswith("_"):
        note_type = "indeks"
    elif "TABLICA" in file_path.name.upper() or re.search(r"norm_table:\s*[\"']?([0-9A-Za-z\.]+)[\"']?", yaml_text):
        note_type = "tablica"
    elif "RYSUNEK" in file_path.name.upper() or "RYS." in file_path.name.upper() or re.search(r"norm_drawing:\s*[\"']?([0-9A-Za-z\.]+)[\"']?", yaml_text):
        note_type = "rysunek"

    # Images
    images = []
    for m in IMG_PATTERN.finditer(content):
        img = m.group(1) or m.group(2)
        images.append(img)

    # SVGs
    svgs = []
    for m in SVG_PATTERN.finditer(content):
        s = m.group(1) or m.group(2)
        svgs.append(s)

    # Table in markdown
    has_md_table = bool(re.search(r'\|.*?\|.*?\|\r?\n\|(?:\s*[:-]+[-| :]*)\|\r?\n\|.*?\|', body))
    has_html_table = "<table" in body.lower()

    # Status
    if note_type == "indeks":
        status = "indeks"
    elif images:
        status = "wymaga_transkrypcji (ma screeny)"
    elif note_type == "tablica" and (has_md_table or has_html_table):
        status = "gotowa (tabela)"
    elif note_type == "rysunek" and svgs:
        status = "gotowa (wektor SVG)"
    elif len(body.strip()) > 50:
        status = "gotowa (tekst)"
    else:
        status = "pusta / szkic"

    return {
        "file": file_path.name,
        "type": note_type,
        "status": status,
        "images": images,
        "svgs": svgs,
        "has_table": has_md_table or has_html_table
    }

def scan_norm(folder_path):
    folder = Path(folder_path)
    md_files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() == ".md"]
    
    # Check Attachments
    att_dir = folder / "Attachments"
    attachments = []
    if att_dir.exists() and att_dir.is_dir():
        attachments = [f.name for f in att_dir.iterdir() if f.is_file()]

    results = []
    stats = {
        "total_notes": len(md_files),
        "wymaga_transkrypcji": 0,
        "gotowe_tekst": 0,
        "gotowe_tabele": 0,
        "gotowe_rysunki": 0,
        "puste": 0,
        "indeksy": 0
    }

    pending_items = []

    for f in sorted(md_files, key=lambda x: x.name):
        res = analyze_note(f)
        results.append(res)
        
        st = res["status"]
        if "wymaga_transkrypcji" in st:
            stats["wymaga_transkrypcji"] += 1
            pending_items.append({
                "file": res["file"],
                "type": res["type"],
                "images": res["images"]
            })
        elif "gotowa (tekst)" in st:
            stats["gotowe_tekst"] += 1
        elif "gotowa (tabela)" in st:
            stats["gotowe_tabele"] += 1
        elif "gotowa (wektor SVG)" in st:
            stats["gotowe_rysunki"] += 1
        elif "indeks" in st:
            stats["indeksy"] += 1
        else:
            stats["puste"] += 1

    return {
        "norm_folder": str(folder),
        "norm_name": folder.name,
        "stats": stats,
        "attachments_count": len(attachments),
        "pending_items": pending_items
    }

def main():
    parser = argparse.ArgumentParser(description="Audyt stanu transkrypcji notatek w folderze normy")
    parser.add_argument("--norm", "-n", required=True, help="Nazwa lub numer normy (np. 13849-1, 60204-1) lub pełna ścieżka do folderu")
    parser.add_argument("--json", action="store_true", help="Wyjście w czystym formacie JSON")
    args = parser.parse_args()

    roots = [DEFAULT_NORMY_DIR, DEFAULT_DYREKTYWY_DIR, DEFAULT_PRAWO_DIR]
    folder = find_norm_folder(args.norm, roots)

    if not folder:
        print(f"[BLAD] Nie znaleziono folderu odpowiadającego zapytaniu: '{args.norm}'", file=sys.stderr)
        sys.exit(1)

    report = scan_norm(folder)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        st = report["stats"]
        print(f"\n=======================================================")
        print(f"📊 RAPORT TRANSKRYPCJI: {report['norm_name']}")
        print(f"📁 Ścieżka: {report['norm_folder']}")
        print(f"=======================================================")
        print(f"Wszystkich notatek Markdown: {st['total_notes']}")
        print(f"  🔴 Wymaga transkrypcji (screeny): {st['wymaga_transkrypcji']}")
        print(f"  🟢 Gotowe teksty:               {st['gotowe_tekst']}")
        print(f"  🟢 Gotowe tabele:               {st['gotowe_tabele']}")
        print(f"  🟢 Gotowe wektory SVG:          {st['gotowe_rysunki']}")
        print(f"  ⚪ Notatki indeksowe:           {st['indeksy']}")
        print(f"  ⚪ Puste / szkice:              {st['puste']}")
        print(f"Załączniki w Attachments/:      {report['attachments_count']}")
        print(f"-------------------------------------------------------")
        if report["pending_items"]:
            print(f"Lista notatek oczekujących na transkrypcję ({len(report['pending_items'])}):")
            for item in report["pending_items"]:
                imgs = ", ".join(item["images"])
                print(f"  - [{item['type'].upper()}] {item['file']} -> screeny: {imgs}")
        else:
            print("🎉 Wszystkie notatki w tym folderze zostały ustrukturyzowane!")
        print(f"=======================================================\n")

if __name__ == "__main__":
    main()
