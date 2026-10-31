# AGENTS.md / GEMINI.md — NormReader (Trinitec Standards & Legal Knowledge Base)

## Language Policy
- **User Communication**: Always communicate with the user in **Polish** (unless explicitly requested otherwise).
- **Normative Text Transcription (CRITICAL)**: Transcribe standard clauses, tables, and legal acts **strictly in the original language of the source document** (Polish for Polish editions `PN-EN`, English for untranslated `ISO`/`IEC`/`EN` documents). Never translate, paraphrase, or summarize normative text.
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
- **Automation Skill & Scripts**: `.agents/skills/standards-transcriber/` (or `scripts/` in repo root).

---

## 2. Non-Negotiable Guardrails

### 2.1. Iron Rule: Zero Text Alteration ($100\%$ Verbatim)
1. **Word-for-Word Fidelity**: Every clause, subclause, definition, footnote, and normative note must be transcribed **character-for-character**, preserving original punctuation, numbering, list hierarchy, and mathematical symbols.
2. **No Autonomous Translation**: If the source screenshot/PDF is in Polish, transcribe in Polish. If in English, transcribe in English.
3. **Zero Hallucination or Interpretation**: Never inject personal interpretations into normative text. Store engineering commentary exclusively inside the YAML `norm_note:` field or a dedicated callout:
   ```markdown
   > [!NOTE] Komentarz inżynierski:
   > Treść komentarza...
   ```

### 2.2. Archival Source Protection
1. **Never Delete Source Files**: Original raster screenshots (`.png`, `.jpg`, `.webp`) and source PDFs in `Attachments/` are permanent legal/engineering evidence and **must never be deleted or overwritten**.
2. **Clean Note Body**: Once a note is transcribed, replace the raster screenshot embed in the Markdown body with structured text, a Markdown/HTML table, or a vector `.svg` embed. Do **not** wrap the old screenshot in a collapsible callout unless explicitly requested by the user.

---

## 3. Note Architecture & `.base` YAML Schemas

Every note must contain valid YAML frontmatter matching the `Normy.base` / `Dyrektywy.base` / `PrawoPL.base` schema.
- **Quoted Wikilinks**: Every wikilink inside YAML **must** be wrapped in double quotes (e.g., `index: ["[[_PN-EN ISO 13849-1]]"]`).
- **Exact Property Names**: Preserve exact YAML property keys required by `.base` files (including the legacy spelling `norm_in_possesion: true` with a single `s` in the index note).

### 3.1. Standard Index Note (`_<NormNumber> - <Title>.md`)
Location: Root folder of the standard in `31 - Notes - Normy\<Number> - <Title>\`.
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
---
#### 4.1 Cele bezpieczeństwa w projektowaniu

Verbatim clause text...

Cross-references use Obsidian wikilinks:
e.g., zgodnie z wymaganiami [[_14119 - urządzenia ryglujące|ISO 14119]] oraz [[4.3. Określenie wymaganego PLr]].

Embed referenced figures and tables via transclusion:
![[13849-1 - RYSUNEK 1 - Schemat oceny ryzyka]]
![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL)]]

#Safety/OcenaRyzyka/Parametry/PL
```

### 3.3. Table Note (`<NormNumber> - TABLICA <N> - <Title>.md` or `TABLICA <N> - <Title>.md`)
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
---
# Tablica 2 – Poziomy zapewnienia bezpieczeństwa (PL)

| PL | Średnie prawdopodobieństwo wystąpienia uszkodzenia niebezpiecznego na godzinę ($PFH_D$)<br>[1/h] |
| :---: | :---: |
| **a** | $\ge 10^{-5}\text{ do }< 10^{-4}$ |
```

### 3.4. Drawing / Figure Note (`<NormNumber> - RYSUNEK <N> - <Title>.md` or `RYSUNEK <N> - <Title>.md`)
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
---
# Rysunek 1 – Schemat oceny ryzyka/zmniejszania ryzyka

![[Rysunek 1 - Schemat oceny ryzyka.svg|800]]

a Odwołanie do ISO 12100:2010
b Odwołanie do niniejszej części ISO 13849
```

---

## 4. Table & Formula Conversion Standards

1. **Standard Parametric Tables**:
   - Use clean GFM Markdown tables with explicit column alignment (`:---:`, `:---`, `---:`).
   - **PANDOC COMPATIBILITY WARNING**: Do NOT use raw HTML `<table>` for standard tables unless absolutely necessary for complex cell spanning (`colspan`/`rowspan`). Pandoc GUI in PDF engine (`pdflatex` / `xelatex`) drops raw HTML table tags, flattening cells into unformatted text.
   - Format mathematical variables, subscripts, inequalities, and exponents in LaTeX (`$PFH_D$`, `$MTTF_D$`, `$DC_{avg}$`, `$10^{-5}$`, `$T_{10D}$`).
   - Use `<br>` for multi-line cells. Escape literal pipes inside wikilinks in table cells (`\|`).
2. **Tables with Pictograms / Miniatures**:
   - Embed vector icons or High-DPI cleaned images directly inside cells: `![[Tablica 4 - Czubek palca.svg\|90]]` or `![[Piktogram_Zakaz.svg\|50]]<br>**Zakaz**`.
3. **Complex Tables (Multi-Row Headers / Merged Cells)**:
   - When a table contains complex `colspan` or `rowspan` merges that cannot be expressed in Markdown, use **clean semantic HTML `<table>`** (`<thead>`, `<tbody>`, `<tr>`, `<th colspan="...">`, `<td rowspan="...">`), but be aware of Pandoc PDF export limitations.

---

## 5. Graphics, Miniatures & Vector Standards (`Stop & Review` Protocol)

Every technical figure, block diagram, or table thumbnail must adhere to the following principles:

1. **STRICT BAN on AI Image Generation (Imagen / Gemini Image-Gen)**:
   - **NEVER** use generative diffusion models (`image-generator`) to hallucinate or invent new drawings for technical standards. They alter geometry, distort anatomy, and hallucinate dimensional principles (e.g., placing dimension arrows across walls instead of measuring reach depth).
2. **Golden Rule for Drawings & Miniatures**:
   - *"Grafika ma być taka sama tylko z wyższą rozdzielczością, bez szarego pod spodem i z czytelnymi opisami."*
3. **Approved Reconstruction Workflow (Cleaned High-DPI & Clean Vector)**:
   - **Step A — Background Cleaning & Watermark Removal**: Map scanner gray background, paper texture, and watermarks (e.g. PKN, WBY) to pure white `#ffffff` via white-point thresholding/curve clipping without eroding black ink strokes.
   - **Step B — High-DPI Upscaling (4x)**: Upscale the cleaned bitmap using high-order Lanczos/Bicubic resampling with edge sharpening to ensure crisp rendering on 4K/Retina displays and in PDF prints.
   - **Step C — Format Selection**: Save either as High-DPI PNG or as a clean spline SVG (via VTracer on the cleaned binary bitmap).
   - **Step D — Mechanical / Block Diagrams (CAD-SVG)**: For purely geometric, dimensional schematics (such as Rysunek 2), Multimodal LLM Vision-to-CAD authoring with 3 layers (canvas/hatch, contours, ISO 129 dimensions) remains valid.
4. **Zero Legend Duplication**:
   - When labels, dimension definitions ($a, b, c$), and legend items ($1, 2, 3$) are already legibly present inside the figure or drawing card, **do NOT duplicate them as text underneath the image**.
5. **PDF Vector Extraction First (When Source PDF Exists)**:
   - If the vector source PDF of the standard is present in the folder, first attempt direct lossless vector extraction via `pdftocairo -svg -f <page> -l <page> "<norm.pdf>" "<out.svg>"`.
6. **STOP & REVIEW Gate**:
   - Present the original raster screenshot side-by-side with the restored/vectorized preview and ask:
     > *"Czy zatwierdzasz grafikę dla Rysunku / Tablicy X, czy wprowadzić poprawki?"*
   - Save the final asset in `Attachments/` and link it only after explicit user approval.

---

## 6. Tag Taxonomy Policy (`tags_catalog.json`)

1. **Catalog Adherence**:
   - Both YAML `tags:` (without `#` prefix) and inline paragraph tags (`#Category/Subcategory`) must strictly match approved entries in `scripts/tags_catalog.json`.
   - **Corrupted Prefix Warning**: Never use truncated tag artifacts present in legacy scans (such as `Safety/OcenaRyzyka/FunkcjaBezpiecze` or `Dyrektywy/OcenaZgodno`); always use the complete Polish word form (e.g., `Safety/OcenaRyzyka/FunkcjaBezpieczeństwa`, `Dyrektywy/OcenaZgodności`).
2. **Approval Gate for New Tags**:
   - Never invent or apply a new tag outside `tags_catalog.json` autonomously. Always ask first:
     > *"Dla tego punktu proponuję dodanie nowego tagu `#Safety/...`. Czy wyrażasz zgodę?"*

---

## 7. Context Protection & Automation Runbook

Never dump entire multi-page PDFs or read all files in a standard's folder manually into the LLM context. Always execute the local Python CLI tools in UTF-8 mode:

1. **Step 1 — Audit Standard Status**:
   ```powershell
   python ".agents/skills/standards-transcriber/scripts/scan_norm.py" --norm "13849-1"
   ```
   Identifies total notes, completed texts/tables/SVGs, and the exact list of notes still containing raster screenshots.
2. **Step 2 — Transcribe & Structure**:
   Process pending notes one by one (or in small logical batches) following Sections 2–6.
3. **Step 3 — Validate SVG Syntax & Visual Fidelity**:
   ```powershell
   python ".agents/skills/standards-transcriber/scripts/svg_generator.py" --validate "Path/To/Attachments/Rysunek_1.svg"
   ```
   Followed by multimodal visual comparison of the rendered SVG against the original screenshot.
4. **Step 4 — Verify Note Integrity**:
   ```powershell
   python ".agents/skills/standards-transcriber/scripts/verify_transcription.py" --file "Path/To/Note.md"
   ```
   Ensure $0$ critical YAML/link errors and $0$ unreplaced screenshot warnings before reporting completion.
5. **Step 5 — Git Stage & Selective Commit**:
   ```powershell
   git status --short
   git diff --stat
   ```
   Stage only verified files and create an atomic Polish Conventional Commit.

---

## 8. Pre-Completion Quality Gate Checklist

Before presenting any completed section or note to the user, verify:
- [ ] **Data Truth ($100\%$ Verbatim)**: All text matches the scan word-for-word in the original language; zero paraphrasing, translations, or missing footnotes.
- [ ] **Graphics Quality & Fidelity**:
  - Drawings & miniatures have pure white background (`#ffffff`), 0% gray scanner noise, and 0% watermarks (PKN/WBY).
  - High-DPI resolution (sharp on 4K and in PDF).
  - Zero AI image generation hallucinations.
  - Zero legend duplication under notes when already present inside drawing cards.
- [ ] **XML / SVG Integrity**: Vector files pass `svg_generator.py --validate` with proper XML entity escaping (`&lt;`, `&gt;`, `&amp;`).
- [ ] **YAML & `.base` Compliance**: Required properties (`norm_number`, `norm_point` / `norm_table` / `norm_drawing`, `norm_in_possesion`) are present and all wikilinks in YAML are enclosed in double quotes (`index: ["[[...]]"]`).
- [ ] **Tag Consistency**: Every YAML and inline tag exists in `tags_catalog.json` (using full Polish words, never truncated prefixes).