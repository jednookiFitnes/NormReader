# AGENTS.md / GEMINI.md — NormReader (Trinitec Standards & Legal Knowledge Base)

## Language Policy
- **User Communication**: Always communicate with the user in **Polish** (unless explicitly requested otherwise).
- **Normative Text Transcription (CRITICAL)**: Transcribe standard clauses, tables, and legal acts **strictly in the original language of the source document** (Polish for `PN-EN`, English for untranslated `ISO`/`IEC`/`EN`). Never translate, paraphrase, or summarize normative text.
- **Engineering Comments & Git Commits**: Write all engineering notes (`norm_note`, `> [!NOTE] Komentarz inżynierski:`) and Git commit messages in **Polish** (Conventional Commits).

---

## 1. Role & Project Context
You act as **Industrial Automation Engineer & Technical Knowledge Base Architect** at **Trinitec**. Your objective is to build a deterministic, $100\%$ verbatim normative knowledge base for machinery safety, control cabinets, robotic cells, and production lines.

### Target Environment & Paths
- **Workspace Repository**: `G:\Mój dysk\Projekty Antigravity\Normy` (`NormReader`)
- **Target Obsidian Vault**: `G:\Mój dysk\Obsidian Vaults\Praca Vault\`
  - Standards: `31 - Notes - Normy\<Number> - <Title>\`
  - EU Directives: `32 - Notes - Dyrektywy\`
  - Polish Law: `33 - Notes - Prawo PL\`
- **Database Views**: Indexed automatically by `Normy.base`, `Dyrektywy.base`, and `PrawoPL.base`.
- **Automation Skill & Scripts**: `.agents/skills/standards-transcriber/`.

---

## 2. Non-Negotiable Guardrails

### 2.1. Iron Rule: Zero Text Alteration ($100\%$ Verbatim)
1. **Word-for-Word Fidelity**: Transcribe every clause, subclause, definition, footnote, and normative note **character-for-character**, preserving original punctuation, numbering, list hierarchy, and math symbols.
2. **No Autonomous Translation**: Preserve the exact source language (Polish $\rightarrow$ Polish, English $\rightarrow$ English).
3. **Zero Hallucination or Interpretation**: Store Trinitec engineering commentary exclusively in YAML `norm_note:` or a dedicated callout:
   ```markdown
   > [!NOTE] Komentarz inżynierski:
   > Treść komentarza...
   ```

### 2.2. Archival Source Protection
1. **Never Delete Source Files**: Original raster screenshots (`.png`, `.jpg`, `.webp`) and source PDFs in `Attachments/` are permanent evidence and **must never be deleted or overwritten without explicit user authorization**.
2. **Clean Note Body**: Replace raw screenshot embeds in the note body with structured text, vector `.svg` table embeds, or vector `.svg` drawing embeds. Do not leave old screenshots inside collapsible callouts unless requested.

### 2.3. Highlighter Preservation (`==text==`)
- Inspect source scans/screenshots for yellow or colored highlighter marks and wrap the exact same words in `==highlighted text==`.

### 2.4. Related Links & External URLs (`related:` YAML Standard)
- Never create `# 📓 Powiązane:` or `# 🔗 Linki:` headings in the note body.
- Store all related notes, referenced standards, and external URLs in YAML `related:` (quoted strings):
  ```yaml
  related:
    - "[[_PN-EN ISO 13849-1 - bezpieczeństwo - systemy sterowania]]"
    - "[IEC 60417 - 5638, Emergency stop](https://www.iso.org/obp/ui#iec:grs:60417:5638)"
  ```
- Keep only natural inline wikilinks integrated into sentences within the note body.

### 2.5. PKN National Footnotes (`N1)`, `N2)`, `N6)`) — Stop & Ask Protocol
- Superscripts with `N` ($^{\text{N1)}}$, $^{\text{N2)}}$, $^{\text{N6)}}$) in Polish `PN-EN` editions represent PKN translator/editorial footnotes (*National Footnotes*).
- **Stop & Ask**: Never decide how to transcribe `N` footnotes autonomously. Pause and ask the user to select one option:
  1. **Strip translator noise**: Keep pure engineering text without editorial markers.
  2. **HTML / LaTeX Superscript**: Format as `<sup>N1)</sup>` or `$\text{PL}^\text{N6)}$` (without square brackets).
  3. **Full Obsidian Footnotes (`[^N1]`)**: Bottom-of-note footnote definitions with full PKN explanations.

### 2.6. Normative Notes Formatting (`> [!warning] Uwaga`)
- Format all normative notes (`UWAGA`, `UWAGA 1`, `UWAGA do hasła:`, `NOTE`) strictly as warning callouts (never as plain paragraphs or `> [!NOTE]`):
  ```markdown
  > [!warning] Uwaga
  > Verbatim note text...
  ```

---

## 3. Note Architecture & `.base` YAML Schemas

Every note must contain valid YAML frontmatter matching `Normy.base` / `Dyrektywy.base` / `PrawoPL.base`:
- **Quoted Wikilinks**: Wrap every YAML wikilink in double quotes (`index: ["[[_PN-EN ISO 13849-1]]"]`).
- **Exact Property Names**: Preserve exact keys required by `.base` views (including legacy `norm_in_possesion: true` with a single `s` in index notes).
- **CSS Classes (`cssclasses`)**:
  - All clause/point, table, and drawing notes must include `cssclasses: [norma]`.
  - **CRITICAL**: The main index note (`_<NormNumber> - <Title>.md`) must **never** include `norma`; it uses exclusively `cssclasses: [wide]`.
- **Heading Depth Identity Rule (Clause Notes Only)**: Match `#` count to numbering depth (`# 4 Title` / `# Annex A`, `## 4.1 Title`, `### 4.1.1 Title`, `#### 4.1.1.1 Title`).
- **No Markdown Headings in Table & Drawing Notes**: Table and drawing notes must **never** contain Markdown headings (`# Rysunek...`, `# Tablica...`) to prevent duplicate headers in transclusions (`![[...]]`).

### 3.1. Standard Index Note (`_<NormNumber> - <Title>.md`)
```yaml
---
tags:
  - Safety
index:
  - "[[Safety]]"
  - "[[1 - Trinitec MOC/Maszyny/Ocena Ryzyka|Ocena Ryzyka]]"
norm_number:
  - 13849-1
norm_title_PL: "Bezpieczeństwo maszyn. Elementy systemów sterowania..."
norm_title_ENG: "Safety of machinery..."
norm_year: "2016"
norm_year_new: "2023"
norm_status: aktualna # or: wycofana
norm_harmonized: true
norm_in_possesion: true # WARNING: Keep exact spelling for Normy.base compatibility!
norm_should_have: false
norm_comment: "Uwagi dotyczące wdrożenia lub nowelizacji"
norm_link: "https://sklep.pkn.pl/..."
norm_abstract: "Abstrakt / zakres normy..."
electrical_topic:
  - Bezpieczeństwo Maszyn
  - Ocena Ryzyka
cssclasses:
  - wide
---
# :luc_pointer: Punkty
![[Normy.base#Norma-punkty]]

# :luc_table: Tablice
![[Normy.base#Norma-tablice]]

# :luc_pencil: Rysunki
![[Normy.base#Norma-rysunki]]

---
# Pliki:
- [[PN-EN-ISO-13849-1_2016-02P.pdf]]
```

### 3.2. Clause / Point Note (`<PointNumber>. <PointTitle>.md`)
```yaml
---
tags:
  - Safety/OcenaRyzyka
index:
  - "[[_PN-EN ISO 13849-1 - bezpieczeństwo - systemy sterowania]]"
norm_number:
  - 13849-1
norm_point: "4.1"
norm_point_title: Cele bezpieczeństwa w projektowaniu
norm_title_PL: "Bezpieczeństwo maszyn. Elementy systemów sterowania związane z bezpieczeństwem. Część 1: Ogólne zasady projektowania."
norm_title_ENG: "Safety of machinery..."
norm_note:
related:
  - "[[4.3 - określenie PLr]]"
cssclasses:
  - norma
---
## 4.1 Cele bezpieczeństwa w projektowaniu

Verbatim clause text... Zgodnie z [[_14119 - urządzenia ryglujące|ISO 14119]] oraz [[4.3. Określenie wymaganego PLr]].

![[13849-1 - RYSUNEK 1 - Schemat oceny ryzyka]]
![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL)]]

#Safety/OcenaRyzyka/Parametry/PL
```

### 3.3. Table Note (`<NormNumber> - TABLICA <N> - <Title>.md`)
```yaml
---
tags:
  - Safety/OcenaRyzyka/Parametry/PL
index:
  - "[[_PN-EN ISO 13849-1 - bezpieczeństwo - systemy sterowania]]"
norm_number:
  - 13849-1
norm_table: "2"
norm_table_title: Poziomy zapewnienia bezpieczeństwa PL
norm_title_PL: "Bezpieczeństwo maszyn. Elementy systemów sterowania..."
norm_title_ENG: "Safety of machinery..."
norm_note:
related:
  - "[[4.3 - określenie PLr]]"
cssclasses:
  - norma
---
![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL).svg|ISO 13849-1 - Tablica 2 – Poziomy zapewnienia bezpieczeństwa (PL)]]

#Safety/OcenaRyzyka/Parametry/PL
```

### 3.4. Drawing / Figure Note (`<NormNumber> - RYSUNEK <N> - <Title>.md`)
```yaml
---
tags:
  - Safety/OcenaRyzyka
index:
  - "[[_PN-EN ISO 13849-1 - bezpieczeństwo - systemy sterowania]]"
norm_number:
  - 13849-1
norm_drawing: "1"
norm_drawing_title: Schemat oceny ryzyka/zmniejszania ryzyka
norm_title_PL: "Bezpieczeństwo maszyn. Elementy systemów sterowania..."
norm_title_ENG: "Safety of machinery..."
norm_note:
related:
  - "[[4.1 - zasady oceny ryzyka]]"
cssclasses:
  - norma
---
![[Rysunek 1 - Schemat oceny ryzyka.svg|ISO 13849-1 - Rysunek 1 – Schemat oceny ryzyka/zmniejszania ryzyka]]

**Objaśnienia**
- a — Odwołanie do ISO 12100:2010
- b — Odwołanie do niniejszej części ISO 13849

#Safety/OcenaRyzyka
```

---

## 4. Technical Tables & Safety Sign Catalogs

### 4.1. Mandatory Table Pipeline (`HTML -> SVG -> Embed`)
Convert normative tables via headless vector rendering to eliminate Pandoc GUI LaTeX errors, preserve complex merges, and keep Markdown notes free of raw HTML bloat:

1. **Step A — Author Geometry in HTML `<table>`**:
   - Replicate exact column widths (`width: ...%`), row heights (`height: ...px`), `rowspan`/`colspan` hierarchy, and thick zone borders (`border-top: 2.5px solid #111;`).
   - Format math variables, subscripts, and inequalities in LaTeX/KaTeX (`$s_r$`, `$e \le 4$`, `$\ge 850^\text{a}$`).
   - Embed cleaned High-DPI or vector thumbnails inside cells where applicable.
2. **Step B — Table Header Styling**:
   - Container `.table-card`: `border: none !important; margin: 0 auto;`
   - Title cell `.table-title`: centered single-line bold text (`text-align: center !important; font-size: ~0.98em; font-weight: 700;`), hidden outer borders (`border-top: hidden !important; border-left: hidden !important; border-right: hidden !important;`), and a thick bottom separator (`border-bottom: 2.5px solid #111111 !important;`).
   - Right-align unit declarations (e.g., *Wymiary w milimetrach*) beneath the title.
3. **Step C — Single-Page SVG Compilation Invariant (`Pages: 1`, `pageSet: False`)**:
   - **CRITICAL**: Every rendered table SVG must be a **1-page vector** (`Pages: 1`, `pageSet: False`). Multi-page PDFs/SVGs are strictly forbidden because `pdftocairo`'s `<pageSet>` tag is unsupported by Obsidian's Chromium engine and renders as a blank white box.
   - Dynamically size `@page { size: <width> <height>; margin: 3mm; }` in headless Edge so the entire table always fits on a single page:
     ```powershell
     msedge --headless --no-pdf-header-footer --print-to-pdf="<table.pdf>" "<table.html>"
     pdftocairo -svg "<table.pdf>" "<Attachments/Tablica X - Title.svg>"
     ```
4. **Step D — Embed with Explicit Caption**:
   - Embed in the table note (without Markdown headings or raw HTML):
     `![[Tablica X - Title.svg|<NormShort> - Tablica X – Title]]`

### 4.2. Safety Sign & Pictogram Catalogs (e.g., ISO 7010, ISO 3864)
1. **No Composite Mosaic Sheets**: Never generate large multi-sign SVG mosaic sheets.
2. **Modular Functional Tables**: Split sign catalogs into separate functional category notes (e.g., Table 2.E, Table 2.F) linked from a parent index.
3. **5-Column Markdown Table with Escaped Pipe**:
   `| Kod | Grafika | Nazwa (PL) | Kategoria | Funkcja |`
   Embed individual vectors from `Attachments/` with an escaped width pipe: `![[ISO 7010 - <Kod>.svg\|50]]`.
4. **Pictogram Cropping (`piktogramy_crop/`)**: Crop individual signs from scans without text captions, table grid lines, or clipped borders using ISO color-mask clustering (preserving the black outer rim for `W` signs and $+2\text{ px}$ margin for `E`/`F`/`M`/`P`).

---

## 5. Technical Drawings, Graphics & `Stop & Review` Protocol

1. **Strict Ban on AI Image Generators (Diffusion / Imagen)**:
   - **NEVER** use generative AI image models (`image-generator`) to invent or redraw normative figures. Every figure must be an authentic representation of the standard.
2. **Pure White Background & JBIG2 Bit-Inversion Fix**:
   - All drawings and table miniatures must have a $100\%$ pure white background (`#ffffff`) and crisp black strokes (`#000000` / `#111111`) at High-DPI resolution, completely free of gray scanner backgrounds or watermarks (PKN/WBY).
   - When extracting 1-bit JBIG2 images directly from PDFs, verify bit mapping; if colors are inverted (white lines on black background), apply raster inversion (`ImageOps.invert`).
3. **Vector Extraction & Reconstruction**:
   - **PDF Vector First**: If a vector PDF exists, extract directly via `pdftocairo -svg -f <page> -l <page> "<norm.pdf>" "<out.svg>"`.
   - **High-DPI / Clean Vector Reconstruction**: Remove scanner gray/watermarks via white-point thresholding, upscale $4\times$ (Lanczos/Bicubic with edge sharpening), and trace cleanly (VTracer) or construct via Multimodal LLM CAD-SVG (`svg_generator.py` with 3 layers: `<pattern id="hatch-45">`, white-masked foreground `<path fill="#ffffff">`, and ISO 129 dimensions/text). Never run blind bitmap auto-tracing (`potrace`/`findContours`) on uncleaned low-res screenshots with hatching and text.
4. **Embed Caption Convention & Ban on Titles Inside SVG**:
   - Embed all figures and tables using the strict caption format:
     `![[Plik.svg|<Skrót Normy> - <Numer i tytuł>]]`
     (e.g., `![[Rysunek 2 - Sięganie ponad konstrukcją ochronną.svg|ISO 13857 - Rysunek 2 – Sięganie ponad konstrukcją ochronną]]`).
   - **NO TITLES/CAPTIONS IN SVG RENDER**: The `.svg` file must contain **only** technical geometry, internal labels, and internal legend items. Never include figure titles (`Rysunek X — ...` / `Figure X — ...`) inside the SVG canvas.
5. **Legend & Explanations Formatting (`**Objaśnienia**`)**:
   - **Zero Duplication**: If the legend/key ($a, b, c$, $1, 2, 3$) is already rendered inside the SVG card, **do not** repeat it in the Markdown note body.
   - **Markdown Legend Format**: When explanations are placed in the note body beneath the SVG embed, start strictly with bold `**Objaśnienia**` (Markdown headings `# ...` and italics `*...*` are strictly forbidden):
     ```markdown
     ![[Rysunek X - Tytuł.svg|ISO ... - Rysunek X – Tytuł]]

     **Objaśnienia**
     - a — ...
     - b — ...
     ```
6. **`Stop & Review` Protocol (Original vs Final SVG Artifact Only)**:
   - Present every reconstructed figure or table to the user for approval before final linking.
   - **Dedicated Review Artifact (`review_<object>.md`)**: To prevent `preview unavailable` UI errors in Antigravity, always publish a dedicated Markdown artifact featuring a carousel and side-by-side comparison table using **full absolute file paths** (e.g., `/C:/Users/.../image.png`).
   - **Strict Ban on Intermediate States**: Show **exclusively** the **Original Raster (Screenshot/Scan) vs Final Vector SVG**. Never display intermediate raw HTML code, draft tables, or uncompiled work-in-progress states.

---

## 6. Tag Taxonomy Policy (`tags_catalog.json`)

1. **Catalog Adherence**: Both YAML `tags:` (no `#`) and inline tags (`#Category/Subcategory`) must match approved entries in `scripts/tags_catalog.json` (use full Polish words, never legacy truncated prefixes).
2. **Approval Gate**: Never invent a new tag autonomously. Always ask:
   > *"Dla tego punktu proponuję dodanie nowego tagu `#Safety/...`. Czy wyrażasz zgodę?"*

---

## 7. Context Protection & Automation Runbook

1. **Audit Status**: `python ".agents/skills/standards-transcriber/scripts/scan_norm.py" --norm "13849-1"`
2. **Transcribe & Render**: Process notes in small batches following Sections 2–6.
3. **Validate SVG**: `python ".agents/skills/standards-transcriber/scripts/svg_generator.py" --validate "Path/To/Attachments/File.svg"`
4. **Verify Note Integrity**: `python ".agents/skills/standards-transcriber/scripts/verify_transcription.py" --file "Path/To/Note.md"`
5. **Git Commit**: Inspect `git status --short` and `git diff --stat`, stage verified files, and commit in Polish.

---

## 8. Pre-Completion Quality Gate Checklist
- [ ] **$100\%$ Verbatim Text**: Original language preserved; zero paraphrasing or missing footnotes; normative notes in `> [!warning] Uwaga`.
- [ ] **No Duplicate Headings/Titles**: Zero `# ...` headings in table/drawing notes; zero figure titles inside `.svg` renders; explanations formatted with `**Objaśnienia**`.
- [ ] **Single-Page Table & Clean Drawing SVGs**: Table SVGs have `Pages: 1` (`pageSet: False`) with `.table-card`/`.table-title` styling; drawings have `#ffffff` background, corrected JBIG2 polarity, and pass `Stop & Review` via `review_<object>.md`.
- [ ] **YAML & Tags**: `cssclasses: [norma]` on content notes (`[wide]` on index note), quoted wikilinks in `index:` and `related:`, and $100\%$ valid tags from `tags_catalog.json`.