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
6. **Odsyłacze krajowe tłumacza PKN (Stop & Ask):**
   - Gdy na skanach polskich norm (PN-EN, PN-EN ISO) pojawią się odsyłacze krajowe tłumacza oznaczone literą N (np. $^{N1)}$, $^{N2)}$, $^{N6)}$), nie podejmuj decyzji autonomicznie. Zawsze zapytaj użytkownika o wybór wariantu: (1) usunięcie szumu redakcyjnego tłumacza, (2) indeks górny HTML (`<sup>N1)</sup>`), czy (3) pełne przypisy Obsidian (`[^N1]`).

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
2. **Detekcja zakreślacza (`==tekst==`) oraz odsyłaczy krajowych ($N$):**
   - Zbadaj zrzut ekranu pod kątem obecności żółtego zakreślacza tekstu (np. filtr RGB markera: $R > 210, G > 210, B < 140$). Dokładnie te same fragmenty tekstu zakreślaj w transkrybowanym Markdown za pomocą składni Obsidiana: `==wyróżniony tekst==`.
   - Zidentyfikuj ewentualne odsyłacze krajowe tłumacza PKN ($^{N1)}$, $^{N6)}$) i zapytaj użytkownika o pożądany wariant formatowania przed zapisaniem notatki.
3. Przepisz tekst w 100% dosłownie.
4. Formatuj nagłówek punktu (np. `#### 4.1 Cele bezpieczeństwa w projektowaniu`).
5. Wykrywaj odniesienia do innych norm i twórz naturalne wikilinki w tekście:
   - np. `zgodnie z wymaganiami [[_14119 - urządzenia ryglujące|ISO 14119]]`
   - np. `patrz [[4.3. Określenie wymaganego PLr]]`
   - Pozostałe powiązane normy, punkty oraz linki zewnętrzne WWW (np. do ISO OBP, IEC) umieszczaj w parametrze YAML `related:` (zakaz tworzenia nagłówków Markdown `# 📓 Powiązane:` oraz `# 🔗 Linki:` w treści notatki).
6. Odwołania do rysunków i tabel osadzaj transkluzją:
   - `![[13849-1 - RYSUNEK 1 - Schemat oceny ryzyka]]`
   - `![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL)]]`
7. Dodaj precyzyjny tag inline na końcu akapitu (np. `#Safety/OcenaRyzyka/Parametry/PL`).

### Krok 3: Konwersja tabel (Pipeline HTML -> SVG -> Embed)
1. **Zatwierdzony tryb postępowania:**
   - Nie wklejaj surowego, wielostronicowego kodu HTML `<table>` bezpośrednio do notatki docelowej (zaśmieca Markdown i gubi formatowanie w Pandoc GUI LaTeX).
   - Wszystkie tabele konwertuj w ścisłym potoku:
     $$\text{HTML } \langle\text{table}\rangle \longrightarrow \text{Wektorowy PDF (Edge headless)} \longrightarrow \text{Czysty SVG (Cairo)} \longrightarrow \text{Osadzenie embed w notatce}$$
2. **Przygotowanie kodu HTML `<table>`:**
   - **Geometria i układ:** Mierz i odtwarzaj proporcjonalne szerokości (`width: %`) oraz minimalne wysokości wierszy (`height: px`) ściśle według skanu.
   - **Scalenia (`rowspan` / `colspan`):** Odwzorowuj wielopoziomowe nagłówki oraz scalone komórki części ciała i miniatur.
   - **Stylizacja nagłówka tabeli:**
     - Tytuł tabeli w jednym wierszu (`font-size: ~0.98em`, `font-weight: 700`, bez zawijania tekstu).
     - Komórka tytułowa (`<th>`) z `border-top: hidden !important; border-left: hidden !important; border-right: hidden !important; border-bottom: 2.5px solid #111111 !important; padding: 10px 4px 5px 4px;`.
     - *Wymiary w milimetrach* wyrównane do prawej pod tytułem.
   - **Grube linie graniczne:** Zgodnie z normą wyróżniaj granice stref wymiarowych za pomocą styli CSS (`border-top: 2.5px solid #111;`, `border-right: ...`).
   - **Wzory i zmienne:** Formatuj zmienne matematyczne, indeksy i nierówności w LaTeX/KaTeX (`$s_r$`, `$e \le 4$`, `$\ge 850^\text{a}$`).
   - **Miniatury i piktogramy:** Osadzaj oczyszczone miniatury High-DPI lub wektory SVG bezpośrednio w komórkach (z czystym tłem `#ffffff` bez znaków wodnych).
3. **Kompilacja tabeli HTML do pliku SVG:**
   - Użyj skryptu `scripts/render_table_to_svg.py` lub wykonaj polecenia:
     1. Wydruk HTML do PDF: `msedge --headless --no-pdf-header-footer --print-to-pdf=<plik.pdf> <plik.html>` z dopasowanym `@page { size: ...; margin: 3mm; }`.
     2. Konwersja do SVG: `pdftocairo -svg <plik.pdf> <plik.svg>`.
   - Zapisz wygenerowany plik `.svg` w folderze `Attachments/` danej normy.
4. **Osadzenie w notatce z podpisem (Embed Caption Convention):**
   - W notatce tabeli wstaw czysty embed z podpisem wg wzorca:
     `![[Tablica X - Nazwa.svg|<Skrót Normy> - Tablica X – Tytuł]]`
     np.: `![[Tablica 4 - sięganie przez otwory o regularnym kształcie - od 14lat.svg|ISO 13857 - Tablica 4 – Sięganie przez otwory o regularnym kształcie – Osoby w wieku od 14 lat]]`
   - **Kategoryczny zakaz dodawania nagłówków Markdown (`# ...`)**: Notatka tabeli nie może zawierać nagłówka Markdown `# Tablica...` (tytuł tabeli znajduje się już w nazwie pliku oraz na wyrenderowanej karcie SVG tabeli). Notatka zawiera wyłącznie czysty embed SVG oraz tagi.

### Krok 4: Przerysowanie / rekonstrukcja rysunku i pętla Stop & Review
1. **Wybór metody rekonstrukcji:**
   - **Ryciny konstrukcyjne / schematy geometryczne (np. Rysunek 2):** Generuj czysty kod wektorowy CAD-SVG (techniczna estetyka inżynierska, czarne linie 1.5–2px, font sans-serif, czytelność w trybie ciemnym i jasnym, wzorzec `<pattern id="hatch-45">`).
   - **Szkice anatomiczne / miniatury tabel / ryciny ze skanów:** Zastosuj procedurę laboratoryjnej rekonstrukcji:
     1. Usunięcie tła i znaków wodnych (white-point ramp do `#ffffff`).
     2. Skalowanie 4x Lanczos + UnsharpMask.
     3. Zapis do High-DPI PNG lub wektoryzacja binarnego oczyszczonego obrazu przez VTracer (spline mode).
2. **Bezpieczeństwo XML:** Upewnij się, że znaki nierówności (`<`, `>`) oraz ampersand (`&`) są poprawnie escapowane (`&lt;`, `&gt;`, `&amp;`), korzystając z metody `add_text()` z `svg_generator.py`.
3. Sprawdź poprawność XML:
   ```powershell
   python scripts/svg_generator.py --validate "<ścieżka.svg>"
   ```
4. **Zaprezentuj zestawienie użytkownikowi bezpośrednio w Antigravity (Tylko Oryginał vs Końcowy SVG):**
   - Wyświetl porównanie bezpośrednio w czacie Antigravity wyłącznie jako: **oryginalna grafika (zrzut ekranu/skan) vs końcowa grafika wektorowa SVG** (np. za pomocą karuzeli lub side-by-side).
   - Zakaz prezentowania stanów pośrednich (np. roboczego kodu HTML, tabel roboczych).
   - Zapytaj: *"Czy zatwierdzasz grafikę / tabelę SVG dla Rysunku / Tablicy X, czy wprowadzić poprawki?"*.
5. Po zatwierdzeniu:
   - Zapisz plik `Rysunek X - Tytuł.svg` w folderze `Attachments/` danej normy.
   - W notatce `RYSUNEK X...md` wstaw odwołanie z podpisem:
     `![[Rysunek X - Tytuł.svg|<Skrót Normy> - Rysunek X – Tytuł]]`
     np.: `![[Rysunek 2 - Sięganie ponad konstrukcją ochronną.svg|ISO 13857 - Rysunek 2 – Sięganie ponad konstrukcją ochronną]]`
6. **Kategoryczny zakaz nagłówków Markdown (`# ...`) i brak duplikacji objaśnień (Zasada czystego widoku):**
   - W notatkach rysunków **kategorycznie zabrania się dodawania nagłówków Markdown (`# ...`)** (tytuł rysunku jest zawarty bezpośrednio na karcie graficznej SVG oraz w nazwie pliku notatki; nagłówki Markdown powodują niepotrzebną duplikację przy transkluzjach `![[...]]`).
   - Jeśli objaśnienia/legenda rysunku (np. $a$, $b$, $c$, 1, 2, 3) są już zawarte wewnątrz wektora SVG na karcie graficznej, **nie przepisuj ich ponownie w treści notatki Markdown pod rysunkiem**.
   - Notatka rysunku zawiera wyłącznie frontmatter YAML, czyste osadzenie wektora z podpisem oraz tagi inline na końcu.

### Krok 5: Uzupełnienie metadanych YAML
Upewnij się, że notatka zawiera komplet pól wymaganych przez `Normy.base` oraz klasę stylów:
- **Obowiązkowa klasa cssclasses:** Wszystkie notatki punktów, tablic i rysunków muszą posiadać `cssclasses:\n  - norma`. **Kategoryczny zakaz dodawania klasy `norma` do głównej notatki indeksowej normy (`_*.md`)!** Notatka główna/indeksowa posiada wyłącznie `cssclasses:\n  - wide`, aby nie zaburzać renderowania widoków baz `.base`.
- **Punkt:** `norm_number`, `norm_point`, `norm_point_title`, `norm_title_PL` (lub `norm_title_ENG` dla norm angielskich), `index: ["[[_NotatkaGlowna]]"]`, `related: ["[[...]]", "[Link](URL)"]`, `tags: [...]`, `cssclasses: [norma]`.
- **Tablica:** `norm_number`, `norm_table`, `norm_table_title`, `norm_title_PL` (lub `ENG`), `index`, `related`, `tags`, `cssclasses: [norma]`.
- **Rysunek:** `norm_number`, `norm_drawing`, `norm_drawing_title`, `norm_title_PL` (lub `ENG`), `index`, `related`, `tags`, `cssclasses: [norma]`.
- **Standard parametru `related:` w YAML:** Wszystkie powiązane notatki, normy oraz linki zewnętrzne WWW (np. ISO OBP) umieszczaj wyłącznie w liście `related:`. Obowiązuje **kategoryczny zakaz tworzenia nagłówków Markdown `# 📓 Powiązane:` oraz `# 🔗 Linki:` w treści notatki**.

### Krok 6: Weryfikacja jakościowa
Uruchom skrypt walidacyjny:
```powershell
python "<ścieżka_do_skilla>/scripts/verify_transcription.py" --file "<ścieżka_do_notatki.md>"
```
Upewnij się, że nie ma błędów krytycznych ani niezgodności z taksonomią tagów.

### Krok 7: Higiena i czyszczenie folderu `Attachments/` (Procedura Stop & Verify)
Po ukończeniu i zatwierdzeniu transkrypcji wszystkich punktów, tabel i rysunków w normie:
1. Przeskanuj folder `Attachments/` pod kątem nieużywanych, osieroconych plików graficznych raster (`.png`, `.jpg`), które zostały zastąpione przez czysty tekst, tabele lub wektory `.svg`.
2. **Kategoryczny zakaz automatycznego usuwania plików bez zgody:**
   - Przygotuj i przedstaw użytkownikowi w oknie czatu dokładną listę plików planowanych do usunięcia (wraz z informacją o ich rozmiarze i braku referencji w notatkach normy).
   - Zapytaj: *"Czy autoryzujesz usunięcie powyższych X nieużywanych plików z folderu Attachments?"*
3. Dopiero po uzyskaniu jednoznacznej autoryzacji użytkownika (np. „autoryzuję”, „zatwierdzam”) wykonaj bezpieczne usunięcie plików.

---

## 🛠️ Narzędzia pomocnicze w katalogu `scripts/`

- `scan_norm.py` – Inwentaryzacja i stan transkrypcji wybranej normy.
- `tags_catalog.json` – Kompletny słownik ponad 210 zatwierdzonych tagów w skarbcu.
- `svg_generator.py` – Szablony inżynierskie SVG oraz walidator poprawności XML z automatycznym escapowaniem `<, >, &`.
- `render_table_to_svg.py` – Deterministyczna kompilacja tabel HTML do wektorowego SVG/PDF/PNG przez Chromium headless i pdftocairo.
- `verify_transcription.py` – Audyt zgodności notatki z bazami `.base`, obsługa formatów list YAML oraz braku osieroconych zrzutów ekranu.
