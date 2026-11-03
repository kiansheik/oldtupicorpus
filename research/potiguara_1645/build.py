#!/usr/bin/env python3
"""Line-level preliminary copular audit of the 1645 Camarão letters.

Source: Navarro (2022), CC BY. The justalinear Tupi/Portuguese lines are copied
from the open-access SciELO edition. Case analyses are research hypotheses,
NOT philologically approved corpus source edits.

Run: python research/potiguara_1645/build.py
Requirements: pip install requests beautifulsoup4
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from demonstratives import augment

HERE = Path(__file__).resolve().parent
URL = "https://www.scielo.br/j/bgoeldi/a/vy7RnrNvd5B4rrCCX6vVx4d/?format=html&lang=pt"
DOI = "https://doi.org/10.1590/2178-2547-BGOELDI-2021-0034"

# Cumulative ordinal (occ) disambiguates repeated identical starts in one letter.
# kind: nominal / property; strategy: deictic_between / deictic_attached /
# zero / eko_predicative. A clause can span several published justalinear lines.
# Comitative/locative uses of ekó and aspectual auxiliaries are excluded.
CASES = """letter|start|end|kind|strategy|occ|note
1|Opamenhẽ pe rubetéramo|gûitekóbo é|nominal|eko_predicative|1|Father identity expressed via -ramo + ekó
1|N’i katuî nhẽ kó|N’i katuî nhẽ kó|property|zero|1|Negative property predication
1|Sasyeté ã|Sasyeté ã|property|deictic_attached|1|Deictic after stative, NOT an identity copula
1|kó yby poretéramo|pe rekóreme|nominal|eko_predicative|1|Inhabitants of this land
1|Na saûsubarypyramo ruã|sekóû|nominal|eko_predicative|1|Negative simulative predicate
1|kó yby poretéramo|ãgûa rekóreme|nominal|eko_predicative|2|Inhabitants of this land, repeated
1|sobaîygûaramo|sekóreme|nominal|eko_predicative|1|Foreigners, as residents of the other side
1|Kó nhõ pe posanga|Kó nhõ pe posanga|nominal|zero|1|This alone is your remedy
1|xe rorybeténe|xe rorybeténe|property|zero|1|I will be happy (class-II predicate)
1|Kó marana|amõ armada rekopûera îabé|nominal|zero|2|This war like former armada, simile not equation
1|akûeîba’e rekó|akûeîba’e rekó|nominal|zero|1|Its condition is that one's condition
1|i mokanhemetepyramo nhẽ|sekóûne|nominal|eko_predicative|1|They will be ruined, simulative nominal predicate
1|Xe remimotaramo|peîkóne|nominal|eko_predicative|1|They will be as those I desire
1|i aparypyramo|peîkó|nominal|eko_predicative|1|They are like cripples
2|nde rubetéramo|gûitekóbo é|nominal|eko_predicative|1|As your true father
2|Nde rubetéramo|gûitekóbo|nominal|eko_predicative|2|As your true father, second occurrence
2|christãoramo|nde rekóreme|nominal|eko_predicative|1|As a Christian
2|Nde reté é ã|Nde reté é ã|property|deictic_attached|1|You are genuine; ã after predicate
2|nde remikugûakaturamo|sekóû|nominal|eko_predicative|1|Known to you, simulative
2|A’e endébe|nhe’engabyeteeté|nominal|zero|1|They are greatly transgressors, anaphoric A'e
2|Na karaíba ruã ixé|Na karaíba ruã ixé|nominal|zero|1|I am not a white man
2|Nde ruba é ã ixé|Nde ruba é ã ixé|nominal|deictic_between|1|DEMONSTRATIVE between nominal father and pronoun I
2|Aîpó pe rekó|îabaibangáî|property|zero|1|That procedure is not difficult; rekó is nominal
3|nde anametéramo|gûitekóbo é|nominal|eko_predicative|1|As your true family member
3|tekó kugûaparamo|gûitekóbo é|nominal|eko_predicative|1|As one who knows the customs
3|opabenhẽ pe rubetéramo|gûitekóbo é|nominal|eko_predicative|1|As your true father
3|N’iî abaibangaî|N’iî abaibangaî|property|zero|1|Not difficult
3|Koba’e tekó|ma’egûasueté|nominal|zero|1|That action is a grand thing
3|xe rorybeté|gûitekóbo|property|eko_predicative|1|Being happy
3|Aîpó nhõ|xe nhe’enga endébe|nominal|zero|1|Only these are my words
3|Na apŷabaíba|irã ereîkóne|property|eko_predicative|1|No longer as formerly treated, comparative-state ekó (borderline)
4|aîkó xe kane’õramo|aîkó xe kane’õramo|property|eko_predicative|1|I am tired; property+ramo
4|nde ipó ahẽ|nde ipó ahẽ|nominal|zero|1|You are theirs, perhaps postpositional possession, uncertain
4|Sorybeté niã|opabenhẽ karaibetá|property|zero|1|All whites happy, niã not ã
4|Nde sema|abaíme|property|zero|2|Your departure is difficult
5|xe rorykatu ã|xe rorykatu ã|property|deictic_attached|1|I am very happy
5|xe abé ã|gûitekóbo|property|eko_predicative|1|I am also not doing badly, ã is presentational
5|Xe ã|nde anama retekatu|nominal|deictic_between|1|DEMONSTRATIVE between I and your true relative
5|Karaíba|na okanhemba’e ruã|nominal|zero|1|Whites are not the lost ones
5|Cristãoramo|sekóreme|nominal|eko_predicative|3|Being Christians
5|Tekokuabe’ymamo|eîkóbo|property|eko_predicative|1|Being in an ignorant state, -ramo and ekó
5|Xe putubabeté ã gûitekóbo|Xe putubabeté ã gûitekóbo|property|eko_predicative|1|Stative plus ekó, with emphatic ã
5|na pe anama ruãtepe oré|na pe anama ruãtepe oré|nominal|zero|1|Are we not your relatives?
5|oré rorybetémo|oré rorybetémo|property|zero|1|We would be very glad
6|Xe rorykatu ã|Xe rorykatu ã|property|deictic_attached|1|I am very happy
6|xe abé ã|gûitekóbo|property|eko_predicative|1|I also am not doing badly, ã is presentational
6|Na oré anama ruãtepiã peẽ|Na oré anama ruãtepiã peẽ|nominal|zero|1|Are you not our relatives?
6|Peẽ cristão-ramo|pe rekoruînhẽ|nominal|eko_predicative|1|As Christians in a bad condition (uncertain segmentation)
6|Erima’e|cristão rekóû|nominal|eko_predicative|1|They used to be Christian, verb ekó
6|naeté katupe|naeté katupe|property|zero|1|You are truly in the open, tentative
"""

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return " ".join(re.findall(r"[a-z0-9]+", "".join(c for c in value if not unicodedata.combining(c))))

def scrape_justalinear():
    """Fetch an independently hosted, text-layer copy of the open-access edition.

    SciELO's web site blocks automated GitHub runners (HTTP 403). Wikimedia hosts
    the freely available 50-page original PDF; extract each justalinear source
    line using the printed || alignment marker. Use the UFOPA copy as fallback.
    """
    import fitz  # PyMuPDF

    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/TRANSCRI%C3%87%C3%83O_E_TRADU%C3%87%C3%83O_INTEGRAL_ANOTADA.pdf",
        "https://arquivos-producao.ufopa.edu.br/arquivos/202310017675e5666416aa70b73ebbcd/transcricaonavarro.pdf",
    ]
    errors = []
    for url in urls:
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; OldTupiCorpus/1.0; academic research)"},timeout=75)
            response.raise_for_status()
            doc = fitz.open(stream=response.content, filetype="pdf")
            rows = []
            seen = set()
            current_letter = 0
            last_heading = (-1, -99)
            for page_idx, page in enumerate(doc):
                content_lines = page.get_text("text", sort=True).splitlines()
                for position, line in enumerate(content_lines):
                    label = line.strip()
                    heading = " ".join(content_lines[max(0,position-2):position+2]).upper()
                    if "TRANSCRIÇÃO COM TRADUÇÃO JUSTALINEAR ANOTADA" in heading:
                        if last_heading[0] != page_idx or abs(position-last_heading[1]) > 3:
                            current_letter += 1
                            last_heading = (page_idx,position)
                    if not (1<=current_letter<=6 and "||" in label and label.count("||")==1):
                        continue
                    tupi, portuguese = [re.sub(r"\s+"," ",chunk).strip().strip("•*– ") for chunk in label.split("||",1)]
                    tupi = re.sub(r"([^\W\d_])\d{1,3}(?=\W|$)",r"\1",tupi,flags=re.UNICODE)
                    tupi = re.sub(r"(?<=\s)\d{1,3}(?=[^\W\d_])","",tupi,flags=re.UNICODE)
                    if not tupi or not portuguese:
                        continue
                    key = (current_letter,normalize(tupi),normalize(portuguese))
                    if key in seen and rows and rows[-1]["letter"]==current_letter and normalize(rows[-1]["tupi"])==normalize(tupi):
                        continue
                    seen.add(key)
                    pos = 1+sum(row["letter"]==current_letter for row in rows)
                    rows.append({"id":f"C{current_letter:02d}-L{pos:03d}","letter":current_letter,"line":pos,
                                 "tupi":tupi,"portuguese":portuguese,"pdf_page":page_idx+1,
                                 "source":DOI,"source_url":url})
            distribution = Counter(x["letter"] for x in rows)
            if set(distribution)==set(range(1,7)) and len(rows)>250:
                return rows,response.content
            errors.append(f"{url}: partial extraction rows={len(rows)}; letters={distribution}")
        except Exception as error:
            errors.append(f"{url}: {type(error).__name__}: {error}")
    raise RuntimeError("No complete machine-readable edition available: "+"; ".join(errors))

def cases():
    result = []
    for line in CASES.strip().splitlines()[1:]:
        fields = line.split("|", 6)
        if len(fields) != 7:
            raise ValueError("Invalid annotation: " + line)
        letter, start, end, kind, strategy, occ, note = fields
        result.append({"id": f"P{len(result)+1:03d}", "letter": int(letter), "start": start, "end": end,
                       "kind": kind, "strategy": strategy, "occurrence": int(occ),
                       "note": note, "evidence_status": "provisional_linguistic_analysis"})
    return result

def annotate(rows, specifications):
    by_letter = defaultdict(list)
    for idx, row in enumerate(rows):
        by_letter[row["letter"]].append((idx,row))
        row.update({"copular": "not_confirmed", "predication_kind": "", "strategy": "",
                    "has_demonstrative_copular_candidate": False,
                    "has_standalone_a_deictic": bool(re.search(r"(?<!\w)ã(?!\w)",row["tupi"])),
                    "has_eko_predicative_candidate": False, "clause_ids": "",
                    "screening": "candidate" if re.search(
                        r"\b(?:sou|és|é|somos|são|estou|estás|está|estão|era|eram|será|serão|estando|ser|estar)\b",
                        row["portuguese"], re.IGNORECASE) or
                        re.search(r"\b(?:ã|ramo|ruã|gûitekóbo|sekóû|sekóreme)\b", row["tupi"], re.IGNORECASE)
                        else "no_automatic_signal",
                    "editorial_status": "unreviewed_negative"})
    extracted, missing = [], []
    for spec in specifications:
        entries = by_letter[spec["letter"]]
        starters = [i for i, (idx,row) in enumerate(entries) if (" " + normalize(spec["start"]) + " ") in (" " + normalize(row["tupi"]) + " ")]
        if len(starters) < spec["occurrence"]:
            missing.append({**spec, "problem": "start not found", "found": len(starters)})
            continue
        first = starters[spec["occurrence"]-1]
        ends = [i for i in range(first, min(first+10, len(entries))) if (" " + normalize(spec["end"]) + " ") in (" " + normalize(entries[i][1]["tupi"]) + " ")]
        if not ends:
            missing.append({**spec, "problem": "end not found", "found_start_id": entries[first][1]["id"]})
            continue
        last = ends[0]
        for j in range(first,last+1):
            row = entries[j][1]
            row["copular"] = "yes_preliminary"
            row["predication_kind"] = ";".join(filter(None, [row["predication_kind"],spec["kind"]]))
            row["strategy"] = ";".join(filter(None, [row["strategy"],spec["strategy"]]))
            row["has_demonstrative_copular_candidate"] |= spec["strategy"] in ("deictic_between","deictic_attached")
            row["has_eko_predicative_candidate"] |= spec["strategy"] == "eko_predicative"
            row["clause_ids"] = ";".join(filter(None, [row["clause_ids"], spec["id"]]))
            row["editorial_status"] = "hypothesis_pending_review"
        extracted.append({**spec, "start_id": entries[first][1]["id"], "end_id": entries[last][1]["id"],
                          "tupi": " ".join(entries[i][1]["tupi"] for i in range(first,last+1)),
                          "portuguese": " ".join(entries[i][1]["portuguese"] for i in range(first,last+1)),
                          "source": DOI})
    for clause in extracted:
        clause["contains_standalone_ã"] = bool(re.search(r"(?<!\w)ã(?!\w)",clause["tupi"]))
    return rows, extracted, missing

def save_csv(path, records, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def main():
    HERE.mkdir(parents=True, exist_ok=True)
    rows, response_content = scrape_justalinear()
    rows, clauses, missing = annotate(rows, cases())
    demonstrative_hits, demo_summary = augment(rows, clauses)
    save_csv(HERE / "all_lines.csv", rows,
             ["id","letter","line","tupi","portuguese","pdf_page","copular","predication_kind","strategy","has_demonstrative_copular_candidate",
              "has_eko_predicative_candidate","has_standalone_a_deictic",
              "demonstrative_candidates","demonstrative_lemmas","demonstrative_candidate_count","has_demonstrative_candidate",
              "related_deictic_particle_candidates","demonstrative_hit_ids",
              "clause_ids","screening","editorial_status","source","source_url"])
    save_csv(HERE / "copular_clauses.csv", clauses,
             ["id","letter","start_id","end_id","tupi","portuguese","kind","strategy","contains_standalone_ã",
              "demonstrative_candidates","demonstrative_lemmas","demonstrative_candidate_count","has_demonstrative_candidate",
              "demonstrative_roles_unreviewed","demonstrative_predication_role","contains_related_particles",
              "note","evidence_status","source"]
    )
    save_csv(HERE / "demonstrative_hits.csv", demonstrative_hits,
             ["hit_id","line_id","letter","surface","lemma","family","inventory_class","provisional_function",
              "preceding_token","following_token","char_start","char_end","tupi","portuguese","clause_ids",
              "copular_context","predication_interposition","editorial_status"])
    save_csv(HERE / "unmatched_annotations.csv", missing,
             ["id","letter","start","end","kind","strategy","occurrence","note","problem","found","found_start_id"])
    strategies = Counter(item["strategy"] for item in clauses)
    nominal_strategies = Counter(item["strategy"] for item in clauses if item["kind"] == "nominal")
    distribution = {str(k): dict(Counter(x["strategy"] for x in clauses if x["letter"] == k)) for k in range(1,7)}
    summary = {"source": DOI, "source_sha256": hashlib.sha256(response_content).hexdigest(),
               "source_pdf": rows[0]["source_url"],
               "row_total": len(rows), "rows_by_letter": dict(Counter(x["letter"] for x in rows)),
               "candidate_clauses_matched": len(clauses), "candidate_clauses_unmatched": len(missing),
               "strategies": dict(strategies), "nominal_strategies": dict(nominal_strategies),
               "strategies_by_letter": distribution, "strict_deictic_between": sum(x["strategy"] == "deictic_between" for x in clauses),
               "all_copular_candidate_clauses_with_standalone_ã": sum(x["contains_standalone_ã"] for x in clauses),
               "annotation_status": "preliminary, not a gold-standard grammatical annotation",
               "demonstrative_inventory": demo_summary}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    (HERE / "README.md").write_text(
        "# Camarão letters (1645): nominal predication audit\n\n"
        "Source: Navarro (2022), \"Transcrição e tradução integral anotada das cartas dos índios Camarões\". "
        + DOI + ". Open-access CC BY.\n\n"
        "**Important:** this is a reproducible pilot analysis and NOT approved philological ground truth. "
        "All six letters' justalinear lines are transcribed to all_lines.csv; only manually tagged hypotheses are labeled "
        "yes_preliminary. A not_confirmed label means unreviewed/untagged, not proven to be non-copular. "
        "Columns beginning with has_ are candidate labels, not grammatical facts.\n\n"
        "Counts count **clauses**, not editorial lines (one clause can span several lines); "
        "strict deictic_between distinguishes the two clear ã-insertion cases from postposed deictics. "
        "Zero strategy means zero overt copular particle, NOT absence of demonstratives. "
        "A full paradigm scan in demonstrative_hits.csv now tracks kó, ikó, aîpó, a’e, koba’e, ebokûé, "
        "kûeî, akûeî and other forms, with nominal-reference roles distinct from the predicative copula hypothesis. "
        "The accompanying summary groups occurrences by lemma, family and letter. "
        "Emphatic é / niã and pronouns with competing readings are inventoried separately. "
        "eko_predicative includes substantive and state predication, NOT ordinary locative, aspectual or possessive rekó. "
        "See summary.json for matched and unmatched annotations.\n\n"
        "Rebuild: pip install requests beautifulsoup4 pymupdf; python research/potiguara_1645/build.py.\n\n"
        "Future review: inspect all candidate rows, disambiguate ã/niã, é, "
        "aé and verb ekó versus demonstrative ikó, then label all clauses and establish verified exhaustive counts.\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if missing:
        print("WARNING: Unmatched manual annotations; see unmatched_annotations.csv. Counts are lower bounds!")

if __name__ == "__main__":
    main()
