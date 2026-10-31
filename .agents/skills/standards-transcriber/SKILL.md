---
name: standards-transcriber
description: >-
  Przepisuj, transkrybuj i strukturyzuj normy techniczne (PN-EN, ISO, IEC), dyrektywy UE
  i akty prawa PL ze zrzutów ekranu oraz plików PDF do postaci czystego tekstu w Obsidianie.
  Gwarantuje 100% dosłowność (Zero Text Alteration) w języku oryginału, konwersję tabel do Markdown / HTML table,
  przerysowywanie rysunków do SVG z procedurą Stop & Review oraz ścisłą spójność z Normy.base i taksonomią tagów.
---

# Standards Transcriber (Workflow Transkrypcji Norm i Aktów Prawnych)

## 📌 Przegląd i zastosowanie

Skill przeznaczony jest do bezbłędnej, deterministycznej transkrypcji i strukturyzacji norm zharmonizowanych (PN-EN, ISO, IEC), dyrektyw Unii Europejskiej oraz polskich ustaw w skarbcu Obsidian firmy Trinitec.

Rozwiązuje dwa główne zadania:
1. **Transkrypcja istniejących notatek opartych na zrzutach ekranu:** Przekształcenie obrazów (`Exported image ...png`, `Pasted Image ...png`) w dosłowny tekst Markdown, tabele oraz grafiki wektorowe SVG.
2. **Przetwarzanie nowych norm (PDF / screeny przekazane przez użytkownika):** Utworzenie nowej struktury folderu, indeksu, notatek punktów, tablic i rysunków w pełnej zgodności z architekturą baz `.base`.

---

## 🛑 Nienaruszalne reguły inżynierskie (Guardrails)

1. **Zero Text Alteration (Zero modyfikacji tekstu):**
   - Ani jedno słowo, liczba, symbol czy znak interpunkcyjny nie może ulec zmianie, skróceniu ani pominięciu.
   - Przepisuj **wyłącznie w języku oryginału** (jeśli norma jest polska – po polsku, jeśli angielska – po angielsku). Zakaz tłumaczenia na własną rękę.
2. **Zachowanie materiałów archiwalnych:**
   - Oryginalne pliki graficzne (`.png`) i PDF w `Attachments/` pozostają nienaruszone.
   - Nie umieszczaj oryginalnych zrzutów w zwijanym calloucie notatki.
3. **Stop & Review dla rysunków:**
   - Każdy rysunek przerysowywany do wektora SVG wymaga **bezwzględnego zatwierdzenia przez użytkownika**. Przed zapisaniem pliku pokaż użytkownikowi zestawienie oryginalnego screena i wygenerowanego SVG.
4. **Zasada bazy tagów:**
   - Stosuj tagi wyłącznie z katalogu `scripts/tags_catalog.json` (ponad 210 pełnych tagów z polskimi znakami diakrytycznymi).
   - Jeżeli pojawia się potrzeba dodania nowego tagu – **zawsze najpierw zapytaj użytkownika o zgodę**.
5. **Nienaruszalność kluczy bazy (`norm_in_possesion`):**
   - W notatkach indeksowych zachowuj dokładną nazwę właściwości `norm_in_possesion: true` (przez jedno `s`) wymaganą przez `Normy.base`. Nigdy nie zamieniaj jej na `norm_in_possession`.

---

## 🚀 Przebieg procedury krok po kroku (Runbook)

### Krok 1: Audyt stanu normy (Ochrona kontekstu)
Zamiast wczytywać wszystkie pliki folderu do prompta, uruchom skaner:
```powershell
python "<ścieżka_do_skilla>/scripts/scan_norm.py" --norm "13849-1"
```
Skrypt zwróci podsumowanie: ile notatek jest gotowych, które pliki zawierają zrzuty ekranu i jakie obrazy są w nich referencjonowane (próg rozpoznania tekstu: >15 znaków).

### Krok 2: Transkrypcja punktu normy
Dla wybranej notatki punktu:
1. Odczytaj oryginalny screen za pomocą `read_file` (lub tekst z PDF).
2. Przepisz tekst w 100% dosłownie.
3. Formatuj nagłówek punktu (np. `#### 4.1 Cele bezpieczeństwa w projektowaniu`).
4. Wykrywaj odniesienia do innych norm i twórz wikilinki Obsidian:
   - np. `zgodnie z wymaganiami [[_14119 - urządzenia ryglujące|ISO 14119]]`
   - np. `patrz [[4.3. Określenie wymaganego PLr]]`
5. Odwołania do rysunków i tabel osadzaj transkluzją:
   - `![[13849-1 - RYSUNEK 1 - Schemat oceny ryzyka]]`
   - `![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL)]]`
6. Dodaj precyzyjny tag inline na końcu akapitu (np. `#Safety/OcenaRyzyka/Parametry/PL`).

### Krok 3: Konwersja tabel
1. **Tabele standardowe i parametryczne:**
   - Twórz w czystym formacie Markdown z wyrównaniem kolumn.
   - Indeksy i wzory matematyczne formatuj w KaTeX (np. `$PFH_D$`, `$\ge 10^{-5}$`).
   - Załamania linii wewnątrz komórek realizuj przez `<br>`.
2. **Tabele z piktogramami / miniaturami:**
   - W komórce tabeli osadzaj grafikę: `![[Piktogram_Zakaz.svg|50]]<br>**Zakaz**`.
3. **Tabele skomplikowane (ze scalonymi nagłówkami lub komórkami `colspan`/`rowspan`):**
   - Stosuj **czysty kod HTML `<table>`** (`<thead>`, `<tbody>`, `<tr>`, `<th colspan="...">`, `<td rowspan="...">`). Obsidian renderuje je bezbłędnie.

### Krok 4: Przerysowanie rysunku i pętla Stop & Review
1. Wygeneruj kod wektorowy SVG (techniczna estetyka inżynierska, czarne linie 1.5–2px, font sans-serif, czytelność w trybie ciemnym i jasnym).
2. **Bezpieczeństwo XML:** Upewnij się, że znaki nierówności (`<`, `>`) oraz ampersand (`&`) są poprawnie escapowane (`&lt;`, `&gt;`, `&amp;`), korzystając z metody `add_text()` z `svg_generator.py`.
3. Sprawdź poprawność XML:
   ```powershell
   python scripts/svg_generator.py --validate "<ścieżka.svg>"
   ```
4. **Zaprezentuj zestawienie użytkownikowi:**
   - Ścieżka do oryginalnego zrzutu ekranu.
   - Kod / wizualizacja nowego wektora SVG.
   - Zapytaj: *"Czy zatwierdzasz przerysowany Rysunek X, czy wprowadzić poprawki?"*.
5. Po zatwierdzeniu:
   - Zapisz plik `Rysunek X - Tytuł.svg` w folderze `Attachments/` danej normy.
   - W notatce `RYSUNEK X...md` wstaw odwołanie: `![[Rysunek X - Tytuł.svg|800]]`.

### Krok 5: Uzupełnienie metadanych YAML
Upewnij się, że notatka zawiera komplet pól wymaganych przez `Normy.base`:
- **Punkt:** `norm_number`, `norm_point`, `norm_point_title`, `norm_title_PL` (lub `norm_title_ENG` dla norm angielskich), `index: ["[[_NotatkaGlowna]]"]`, `tags: [...]`.
- **Tablica:** `norm_number`, `norm_table`, `norm_table_title`, `norm_title_PL` (lub `ENG`), `index`, `tags`.
- **Rysunek:** `norm_number`, `norm_drawing`, `norm_drawing_title`, `norm_title_PL` (lub `ENG`), `index`, `tags`.

### Krok 6: Weryfikacja jakościowa
Uruchom skrypt walidacyjny:
```powershell
python "<ścieżka_do_skilla>/scripts/verify_transcription.py" --file "<ścieżka_do_notatki.md>"
```
Upewnij się, że nie ma błędów krytycznych ani niezgodności z taksonomią tagów.

---

## 🛠️ Narzędzia pomocnicze w katalogu `scripts/`

- `scan_norm.py` – Inwentaryzacja i stan transkrypcji wybranej normy.
- `tags_catalog.json` – Kompletny słownik ponad 210 zatwierdzonych tagów w skarbcu.
- `svg_generator.py` – Szablony inżynierskie SVG oraz walidator poprawności XML z automatycznym escapowaniem `<, >, &`.
- `verify_transcription.py` – Audyt zgodności notatki z bazami `.base`, obsługa formatów list YAML oraz braku osieroconych zrzutów ekranu.
