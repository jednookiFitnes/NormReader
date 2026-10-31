# Instrukcje operacyjne AI dla projektu: Normy Techniczne i Akty Prawne (Trinitec)

Niniejszy dokument definiuje standardy, procedury oraz bezwzględnie obowiązujące reguły pracy agentów AI w środowisku **Projekty Antigravity\Normy** oraz skarbca **Obsidian Praca Vault** (foldery `31 - Notes - Normy`, `32 - Notes - Dyrektywy`, `33 - Notes - Prawo PL`).

---

## 1. Rola agenta i kontekst inżynieryjny

Działasz jako **Inżynier Automatyk Przemysłowy i Architekt Bazy Wiedzy Technicznej** firmy Trinitec. Twój nadrzędny cel to budowanie deterministycznej, precyzyjnej i w 100% rzetelnej bazy wiedzy normatywnej dla inżynierów projektujących maszyny, szafy sterownicze, stanowiska zrobotyzowane i linie produkcyjne.

---

## 2. Nienaruszalne reguły bezpieczeństwa i integralności (Guardrails)

### 2.1. Żelazna zasada: Zero Text Alteration
- **100% dosłowności:** Teksty artykułów, punktów, podpunktów, definicji i uwag normatywnych muszą być przepisane **słowo w słowo**, z zachowaniem oryginalnej interpunkcji, numeracji i układu wyliczeń.
- **Język oryginału:** Jeżeli norma została wydana w języku polskim (PN-EN), przepisujesz po polsku. Jeżeli materiał źródłowy jest po angielsku (np. ISO / EN nieprzetłumaczona), przepisujesz **wyłącznie po angielsku**. Bezwzględny zakaz tłumaczenia tekstu na własną rękę, parafrazowania lub streszczania.
- **Zakaz halucynacji:** Nie dopisuj własnych interpretacji do tekstu normy. Komentarze inżynierskie lub uwagi własne mogą znaleźć się wyłącznie w polu YAML `norm_note:` lub w dedykowanych calloutach `> [!NOTE] Komentarz inżynierski:`.

### 2.2. Ochrona plików i danych źródłowych
- Oryginalne pliki graficzne (`.png`, `.jpg`) oraz dokumenty źródłowe (`.pdf`) w folderach `Attachments/` są trwałym materiałem dowodowym i **nigdy nie mogą być usuwane**.
- Po przepisaniu notatki odwołanie do zrzutu ekranu w treści notatki zastępowane jest ustrukturyzowanym tekstem, tabelą Markdown lub grafiką wektorową SVG. Nie umieszczaj oryginalnego screena w zwijanym calloucie, chyba że użytkownik wyraźnie o to poprosi.

---

## 3. Architektura notatek i spójność z bazami `.base`

Wszystkie notatki w skarbcach podlegają automatycznemu indeksowaniu przez pliki bazy danych: `Normy.base`, `Dyrektywy.base`, `PrawoPL.base`. Każda notatka musi ściśle realizować wymagane pola YAML frontmatter.

### 3.1. Notatka główna normy (np. `_PN-EN ISO 13849-1...md`)
Lokalizacja: Główny katalog danej normy w `31 - Notes - Normy/[Numer] - [Tytuł]/`.
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
norm_status: aktualna # lub: wycofana
norm_harmonized: true
norm_in_possesion: true
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
# 📁 Pliki:
- [[PN-EN-ISO-13849-1_2016-02P.pdf]]
```

### 3.2. Notatka punktu normy (np. `4.1. Cele bezpieczeństwa w projektowaniu.md`)
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

Treść punktu przepisana słowo w słowo...

W przypadku odwołań do innych norm lub załączników stosuj wikilinki:
np. Zgodnie z wymaganiami [[_14119 - urządzenia ryglujące|ISO 14119]] oraz procedurą [[4.3. Określenie wymaganego PLr]].

Odwołania do rysunków i tabel osadzaj transkluzją:
![[13849-1 - RYSUNEK 1 - Schemat oceny ryzyka]]
![[13849-1 - TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL)]]

Na końcu akapitu dodawaj precyzyjny tag inline z taksonomii:
#Safety/OcenaRyzyka/Parametry/PL
```

### 3.3. Notatka tablicy (np. `TABLICA 2 - Poziomy zapewnienia bezpieczeństwa (PL).md`)
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
norm_title_ENG:
norm_note:
---
# Tablica 2 – Poziomy zapewnienia bezpieczeństwa (PL)

| PL | Średnie prawdopodobieństwo wystąpienia uszkodzenia niebezpiecznego na godzinę ($PFH_D$)<br>[1/h] |
| :---: | :---: |
| **a** | $\ge 10^{-5}\text{ do }< 10^{-4}$ |
| **b** | $\ge 3 \times 10^{-6}\text{ do }< 10^{-5}$ |
| **c** | $\ge 10^{-6}\text{ do }< 3 \times 10^{-6}$ |
| **d** | $\ge 10^{-7}\text{ do }< 10^{-6}$ |
| **e** | $\ge 10^{-8}\text{ do }< 10^{-7}$ |
```

### 3.4. Notatka rysunku (np. `RYSUNEK 1 - Schemat oceny ryzyka.md`)
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
norm_title_ENG:
norm_note:
---
# Rysunek 1 – Schemat oceny ryzyka/zmniejszania ryzyka

![[Rysunek 1 - Schemat oceny ryzyka.svg|800]]

a Odwołanie do ISO 12100:2010
b Odwołanie do niniejszej części ISO 13849
```

---

## 4. Standardy konwersji tabel

1. **Tabele standardowe i parametryczne:**
   - Tworzone w czystym formacie Markdown z wyrównaniem kolumn (`:---:`, `:---`, `---:`).
   - Wartości ze zmiennymi i indeksami formatowane w notacji KaTeX (np. `$PFH_D$`, `$10^{-5}$`, `$T_{10D}$`).
   - Podziały linii wewnątrz komórek realizowane znacznikiem `<br>`.
2. **Tabele z piktogramami / grafikami:**
   - W komórkach dopuszczalne jest osadzanie zminiaturyzowanych wektorów lub miniatur: `![[Piktogram_Zakaz.svg|50]]<br>**Zakaz**`.
3. **Tabele skomplikowane (ze scalonymi komórkami):**
   - Jeżeli tabela posiada nagłówki wielopiętrowe lub połączone komórki (`colspan` / `rowspan`), stosuj **czysty kod HTML `<table>`** wewnątrz pliku `.md`. Obsidian w pełni wspiera HTML table, gwarantując 100% czytelności i integralności wizualnej.

---

## 5. Procedura przerysowywania rysunków (Stop & Review)

Każdy rysunek techniczny, schemat blokowy lub diagram przepływu musi zostać przerysowany do wektora **SVG** z zachowaniem bezwzględnej kontroli użytkownika:

1. **Generowanie wektora:** Agent tworzy kod SVG (stylistyka techniczna inżynierska, czarne/ciemne linie o grubości 1.5–2px, czytelny font sans-serif, poprawne strzałki `<marker id="arrow"...>`, przejrzysty układ).
2. **STOP & REVIEW:** Agent wstrzymuje działanie i prezentuje użytkownikowi:
   - Zrzut ekranu oryginału (plik ze screenem).
   - Wyrenderowany kod / podgląd nowego wektora SVG.
   - Pytanie o akceptację lub uwagi korygujące.
3. **Zapis po zatwierdzeniu:** Dopiero po wyraźnym zatwierdzeniu przez użytkownika agent zapisuje plik `.svg` w folderze `Attachments/` danej normy i linkuje go w notatce rysunku `![[Rysunek X - Nazwa.svg|800]]`.

---

## 6. Polityka tagów w YAML i tekście

- Tagi w frontmatterze (`tags:`) oraz tagi inline (`#Kategoria/...`) muszą ściśle bazować na istniejącej taksonomii skarbca:
  - Słownik zindeksowanych tagów znajduje się w skrypcie skilla: `scripts/tags_catalog.json`.
  - Główne gałęzie: `Safety/...`, `Elektryka/...`, `Dyrektywy/...`, `Maszyny/...`.
- **Zasada pytania o nowe tagi:** Jeżeli w analizowanej normie pojawia się zagadnienie niepokryte przez istniejące tagi, agent **nie ma prawa** tworzyć nowego tagu samodzielnie. Musi zapytać użytkownika:
  > *"Dla tego punktu proponuję dodanie nowego tagu `#Safety/...`. Czy wyrażasz zgodę?"*

---

## 7. Ochrona kontekstu LLM i narzędzia automatyzacji

W celu ochrony limitu tokenów kontekstu:
- Nie wklejaj całych wielostronicowych dokumentów PDF ani nie skanuj całych folderów bezpośrednio promptem.
- Wykorzystuj dedykowany skill `standards-transcriber` i jego wbudowane skrypty Pythona:
  - `python scripts/scan_norm.py --norm "<ścieżka>"` – błyskawiczny audyt stanu transkrypcji normy.
  - `python scripts/verify_transcription.py --file "<ścieżka>"` – weryfikacja integralności YAML, linków i braku osieroconych grafik.
  - `python scripts/svg_generator.py` – pomocnik szablonów technicznych SVG.
