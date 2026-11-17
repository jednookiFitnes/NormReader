import json
import re
import hashlib
from pathlib import Path

# Paths
PLAN_PATH = Path(r"G:\Mój dysk\Obsidian Vaults\Praca Vault\31 - Notes - Normy\13855_2025 - czas dobiegu\_Plan_przepisania_13855.md")
NORMY_CAT_PATH = Path(r"G:\Mój dysk\Projekty Antigravity\Normy\.agents\skills\standards-transcriber\scripts\tags_catalog.json")
VAULT_CAT_PATH = Path(r"G:\Mój dysk\Obsidian Vaults\Praca Vault\.agents\skills\standards-transcriber\scripts\tags_catalog.json")

def test_tags_catalog_sync():
    print("=== TEST 1: tags_catalog.json Synchronization ===")
    assert NORMY_CAT_PATH.exists(), f"Normy catalog not found at {NORMY_CAT_PATH}"
    assert VAULT_CAT_PATH.exists(), f"Vault catalog not found at {VAULT_CAT_PATH}"
    
    with open(NORMY_CAT_PATH, "rb") as f:
        normy_bytes = f.read()
        normy_hash = hashlib.sha256(normy_bytes).hexdigest()
        
    with open(VAULT_CAT_PATH, "rb") as f:
        vault_bytes = f.read()
        vault_hash = hashlib.sha256(vault_bytes).hexdigest()
        
    print(f"Normy SHA256: {normy_hash} (size: {len(normy_bytes)})")
    print(f"Vault SHA256: {vault_hash} (size: {len(vault_bytes)})")
    
    with open(NORMY_CAT_PATH, "r", encoding="utf-8") as f:
        normy_json = json.load(f)
    with open(VAULT_CAT_PATH, "r", encoding="utf-8") as f:
        vault_json = json.load(f)
        
    normy_tags = set(t for cat in normy_json.get("categories", {}).values() for t in cat)
    vault_tags = set(t for cat in vault_json.get("categories", {}).values() for t in cat)
    
    print(f"Normy unique tags: {len(normy_tags)}, meta total: {normy_json.get('total_tags')}")
    print(f"Vault unique tags: {len(vault_tags)}, meta total: {vault_json.get('total_tags')}")
    
    diff_nv = normy_tags - vault_tags
    diff_vn = vault_tags - normy_tags
    print(f"In Normy but not Vault: {len(diff_nv)}")
    print(f"In Vault but not Normy: {len(diff_vn)}")
    
    assert normy_hash == vault_hash, f"Catalog hashes differ!"
    assert normy_tags == vault_tags, f"Tag sets differ!"
    print("-> RESULT: Catalogs are IDENTICAL and synchronized!\n")
    return normy_tags

def test_cited_tags_in_plan(catalog_tags):
    print("=== TEST 2: Cited Tags in Section 5.1 & Section 3 ===")
    text = PLAN_PATH.read_text(encoding="utf-8")
    
    # Extract Section 5.1 tags
    sec_5_1_match = re.search(r"### 5\.1\. Tagi zatwierdzone z `tags_catalog\.json`.*?\n(.*?)\n### 5\.2", text, re.DOTALL)
    assert sec_5_1_match, "Could not find Section 5.1 in plan"
    sec_5_1_lines = sec_5_1_match.group(1).splitlines()
    
    cited_5_1 = []
    for line in sec_5_1_lines:
        line_s = line.strip()
        if line_s.startswith("- "):
            tag = line_s[2:].strip().strip("`").lstrip("#")
            tag = tag.split()[0].strip("`")
            cited_5_1.append(tag)
            
    print(f"Total tags cited in Section 5.1: {len(cited_5_1)}")
    missing_5_1 = [t for t in cited_5_1 if t not in catalog_tags]
    print(f"Section 5.1 tags missing from catalog: {len(missing_5_1)}")
    if missing_5_1:
        print("Missing in 5.1:", missing_5_1)
    assert len(missing_5_1) == 0, f"Found {len(missing_5_1)} cited tags in Sec 5.1 missing from catalog!"
    
    # Extract tags used in Section 3 tables (3.1 to 3.5)
    sec_3_match = re.search(r"## 3\..*?\n## 4\.", text, re.DOTALL)
    assert sec_3_match, "Could not find Section 3 in plan"
    sec_3_text = sec_3_match.group(0)
    
    # Parse each row of tables in Section 3 to accurately extract the assigned tag column
    assigned_tags_all = []
    proposed_tags_in_sec_3 = set()
    all_units = []
    
    for line in sec_3_text.splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("| Lp."):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            # Skip separator line (all cols only contain -, :, spaces)
            if all(re.match(r"^[:\-\s]+$", c) for c in cols):
                continue
            if len(cols) >= 8:
                all_units.append(cols)
                tag_col = cols[-1]
                # Split multiple tags by comma
                raw_tags = [t.strip() for t in tag_col.split(",")]
                for rt in raw_tags:
                    # Check if enclosed in square brackets `[#Tag]`
                    m_prop = re.match(r"^`?\[#([^\]`]+)\]`?$", rt)
                    if m_prop:
                        tag_name = m_prop.group(1).strip()
                        proposed_tags_in_sec_3.add(tag_name)
                        assigned_tags_all.append(tag_name)
                    else:
                        m_norm = re.match(r"^`?#([^`\s,]+)`?$", rt)
                        if m_norm:
                            tag_name = m_norm.group(1).strip()
                            assigned_tags_all.append(tag_name)
                        else:
                            clean = rt.strip("`").strip()
                            if clean.startswith("[#") and clean.endswith("]"):
                                tag_name = clean[2:-1].strip()
                                proposed_tags_in_sec_3.add(tag_name)
                                assigned_tags_all.append(tag_name)
                            elif clean.startswith("#"):
                                tag_name = clean[1:].strip()
                                assigned_tags_all.append(tag_name)
                        
    unique_sec_3_tags = set(assigned_tags_all)
    print(f"Total units parsed across Section 3 tables: {len(all_units)}")
    assert len(all_units) == 139, f"Expected 139 units in Section 3, got {len(all_units)}"
    
    # Verify continuous Lp numbering from 1 to 139
    lp_numbers = [int(u[0]) for u in all_units]
    assert lp_numbers == list(range(1, 140)), f"Lp numbering is not continuous 1 to 139!"
    print("Continuous unit numbering 1 to 139 verified (100% complete)!")
    
    print(f"Total tag assignments parsed in Section 3: {len(assigned_tags_all)}")
    print(f"Unique tags assigned across Section 3: {len(unique_sec_3_tags)}")
    print(f"Proposed tags (in square brackets `[...]`) in Section 3: {len(proposed_tags_in_sec_3)}")
    for pt in sorted(proposed_tags_in_sec_3):
        print(f"  - #{pt}")
        
    # Check if all non-proposed tags in Section 3 exist in catalog
    existing_in_sec_3 = unique_sec_3_tags - proposed_tags_in_sec_3
    print(f"Existing tags assigned across Section 3: {len(existing_in_sec_3)}")
    missing_existing_sec_3 = [t for t in existing_in_sec_3 if t not in catalog_tags]
    print(f"Existing tags assigned in Section 3 missing from catalog: {len(missing_existing_sec_3)}")
    if missing_existing_sec_3:
        print("Missing existing in Sec 3:", missing_existing_sec_3)
    assert len(missing_existing_sec_3) == 0, f"Found {len(missing_existing_sec_3)} existing tags in Sec 3 missing from catalog!"
    
    print("-> RESULT: All cited tags in Sec 5.1 and all existing tags in Sec 3 exist in catalog (missing = 0)!\n")
    return text, unique_sec_3_tags, proposed_tags_in_sec_3

def test_proposed_tags_concordance(text, proposed_in_sec_3):
    print("=== TEST 3: Proposed Tags Concordance (Section 3 vs Section 5.2) ===")
    sec_5_2_match = re.search(r"### 5\.2\..*?\n## 6\.", text, re.DOTALL)
    assert sec_5_2_match, "Could not find Section 5.2 in plan"
    sec_5_2_text = sec_5_2_match.group(0)
    
    # Parse table in Section 5.2
    # Table rows format: | Lp. | Proponowany nowy tag | Jednostki w ISO 13855:2025 | Techniczne uzasadnienie inżynierskie | Status formalny |
    table_rows = re.findall(r"^\|\s*(\d+)\s*\|\s*`?#?([^`|]+?)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", sec_5_2_text, re.MULTILINE)
    print(f"Found {len(table_rows)} proposed tag rows in Section 5.2 table:")
    
    sec_5_2_tags = {}
    for lp, tag, units, rationale, status in table_rows:
        clean_tag = tag.strip().strip("`").lstrip("#").strip()
        sec_5_2_tags[clean_tag] = {
            "lp": int(lp),
            "units": units.strip(),
            "rationale": rationale.strip(),
            "status": status.strip()
        }
        print(f"  [{lp}] #{clean_tag} -> Units: {units.strip()} (Status: {status.strip()})")
        
    print(f"\nTotal proposed tags in Section 5.2 table: {len(sec_5_2_tags)}")
    print(f"Total proposed tags used in Section 3: {len(proposed_in_sec_3)}")
    
    # Check if any tag in sec_5_2 is missing in sec_3
    orphan_in_5_2 = set(sec_5_2_tags.keys()) - proposed_in_sec_3
    print(f"Tags in Section 5.2 table but NOT in Section 3 (orphaned): {len(orphan_in_5_2)}")
    if orphan_in_5_2:
        print("  Orphaned tags:", orphan_in_5_2)
        
    # Check if any proposed tag used in sec_3 is missing in sec_5_2
    missing_in_5_2 = proposed_in_sec_3 - set(sec_5_2_tags.keys())
    print(f"Tags used in Section 3 but NOT in Section 5.2: {len(missing_in_5_2)}")
    if missing_in_5_2:
        print("  Missing from 5.2:", missing_in_5_2)
        
    # Check syntax of proposed tags
    for tag in sec_5_2_tags:
        assert tag.startswith("Safety/"), f"Tag {tag} does not start with Safety/"
        # PascalCase check on parts
        parts = tag.split("/")
        for p in parts:
            assert p[0].isupper(), f"Segment {p} in tag {tag} is not PascalCase"
            
    assert len(sec_5_2_tags) == 9, f"Expected exactly 9 active proposed tags in Sec 5.2, got {len(sec_5_2_tags)}"
    assert len(proposed_in_sec_3) == 9, f"Expected exactly 9 proposed tags in Sec 3, got {len(proposed_in_sec_3)}"
    assert set(sec_5_2_tags.keys()) == proposed_in_sec_3, "Section 3 and Section 5.2 proposed tags are NOT in 1:1 concordance!"
    
    # Check callout explaining PSPE tags
    pspe_callout = "Wyjaśnienie statusu i genezy propozycji tagów urządzeń czułych na nacisk (PSPE)" in sec_5_2_text
    print(f"PSPE contextual explanation callout present: {pspe_callout}")
    assert pspe_callout, "Missing PSPE explanation callout in Section 5.2"
    
    print("-> RESULT: Concordance between Section 3 and Section 5.2 is 100% (exactly 9 active tags in 1:1 match)!\n")

def test_formula_count_labels(text):
    print("=== TEST 4: Formula Count Labels Verification ===")
    # 1. Section 1.1 count label
    sec_1_1_match = re.search(r"\*\*(\d+)\s*wzorów\s*obliczeniowych\*\*", text)
    print(f"Sec 1.1 formula match: '{sec_1_1_match.group(0)}' -> count: {sec_1_1_match.group(1)}" if sec_1_1_match else "NONE")
    
    # 2. Section 3.5 header label
    sec_3_5_match = re.search(r"### 3\.5\. Kategoria: Wzory Obliczeniowe Normy \((\d+) Wzorów\)", text)
    print(f"Sec 3.5 header match: '{sec_3_5_match.group(0)}' -> count: {sec_3_5_match.group(1)}" if sec_3_5_match else "NONE")
    
    # 3. Section 6 Phase 3 label
    sec_6_phase3_match = re.search(r"FAZA 3:\s*Opracowanie\s*(\d+)\s*wzorów\s*obliczeniowych", text)
    print(f"Sec 6 Phase 3 match: '{sec_6_phase3_match.group(0)}' -> count: {sec_6_phase3_match.group(1)}" if sec_6_phase3_match else "NONE")
    
    # Count actual formulas in Table 3.5
    sec_3_5_table_match = re.search(r"### 3\.5\. Kategoria: Wzory Obliczeniowe Normy.*?\n(\|.*?)(?=\n\n|\n---|\n## 4\.|$)", text, re.DOTALL)
    assert sec_3_5_table_match, "Could not find Table 3.5"
    table_3_5 = sec_3_5_table_match.group(1)
    
    formula_rows = []
    for line in table_3_5.splitlines():
        line = line.strip()
        if line.startswith("|") and not line.startswith("| Lp."):
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if all(re.match(r"^[:\-\s]+$", c) for c in cols):
                continue
            if len(cols) >= 3 and cols[1].startswith("Formula"):
                formula_rows.append(cols)
                
    print(f"Actual parsed formula rows in Table 3.5: {len(formula_rows)}")
    formula_names = [r[1] for r in formula_rows]
    print(f"First 3 formulas: {formula_names[:3]}")
    print(f"Last 5 formulas: {formula_names[-5:]}")
    
    assert len(formula_rows) == 45, f"Expected 45 actual formula rows, found {len(formula_rows)}"
    
    # Verify label values
    assert sec_1_1_match and sec_1_1_match.group(1) == "45", f"Sec 1.1 formula count is not 45: {sec_1_1_match.groups() if sec_1_1_match else None}"
    assert sec_3_5_match and sec_3_5_match.group(1) == "45", f"Sec 3.5 header formula count is not 45: {sec_3_5_match.groups() if sec_3_5_match else None}"
    assert sec_6_phase3_match and sec_6_phase3_match.group(1) == "45", f"Sec 6 Phase 3 formula count is not 45: {sec_6_phase3_match.groups() if sec_6_phase3_match else None}"
    
    print("-> RESULT: All formula count labels (Sec 1.1, Sec 3.5, Sec 6 Phase 3) consistently state 45 formulas!\n")

def test_existing_notes_protection():
    print("=== TEST 5: Integrity of Existing Notes Protection ===")
    norm_dir = Path(r"G:\Mój dysk\Obsidian Vaults\Praca Vault\31 - Notes - Normy\13855_2025 - czas dobiegu")
    md_files = [f for f in norm_dir.glob("*.md") if f.name != "_Plan_przepisania_13855.md"]
    print(f"Total existing .md notes (excluding plan): {len(md_files)}")
    assert len(md_files) == 35, f"Expected 35 existing notes, found {len(md_files)}"
    print("-> RESULT: Exactly 35 existing notes present, zero unwanted deletions or additions.\n")

if __name__ == "__main__":
    cat_tags = test_tags_catalog_sync()
    text, sec_3_tags, proposed_sec_3 = test_cited_tags_in_plan(cat_tags)
    test_proposed_tags_concordance(text, proposed_sec_3)
    test_formula_count_labels(text)
    test_existing_notes_protection()
    print("==================================================")
    print("=== ALL EMPIRICAL VERIFICATION TESTS PASSED!   ===")
    print("==================================================")
