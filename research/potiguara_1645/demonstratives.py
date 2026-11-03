"""Broad and explicitly ambiguous demonstrative inventory for the Camarão letters.

Inventory follows Lemos Barbosa, Curso de Tupi Antigo (1956), §§69–75,
and Navarro's notes to the 2022 Camarão edition (especially note 93 on kó).
This scanner is an inclusive lexical candidate finder, NOT a parser of
copular functions. Forms such as a'e, ã, ikó, aé, niã are polyfunctional.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

# Exact-token forms, never arbitrary substrings. NFC is sufficient because
# Navarro's edition uses composed accents and apostrophes.
FORMS = {
    # Proximal deictics; free / nominalized demonstrative variants
    "ã": ("proximal", "ã"), "ang": ("proximal", "ang"),
    "anga": ("proximal", "ang"), "iã": ("proximal", "iã"),
    "iang": ("proximal", "iã"), "ianga": ("proximal", "iã"),
    "kó": ("proximal_visible", "kó"), "ikó": ("proximal_visible", "ikó"),
    "koa": ("proximal_visible", "kó"), "koba'e": ("proximal_visible", "kó"),
    "kóba'e": ("proximal_visible", "kó"),
    "ikoba'e": ("proximal_visible", "ikó"),
    "ãba'e": ("proximal", "ã"), "angyba'e": ("proximal", "ang"),
    # Medial and interlocutor-centred
    "ebokûé": ("medial_visible", "ebokûé"), "ebokûeî": ("medial_visible", "ebokûeî"),
    "ebokuéi": ("medial_visible", "ebokûeî"), "ebokûea": ("medial_visible", "ebokûé"),
    "ebokûeîa": ("medial_visible", "ebokûeî"),
    "ebokûeîba'e": ("medial_visible", "ebokûeî"),
    "eboûĩ": ("medial_visible", "eboûĩ"), "eboûing": ("medial_visible", "eboûing"),
    "ebogûĩ": ("medial_visible", "eboûĩ"), "ebogûing": ("medial_visible", "eboûing"),
    "ebogûia": ("medial_visible", "eboûĩ"), "ûĩ": ("medial_visible", "ûĩ"),
    "uĩ": ("medial_visible", "ûĩ"),
    "aîpó": ("medial_unseen", "aîpó"), "aipó": ("medial_unseen", "aîpó"),
    "aîpoa": ("medial_unseen", "aîpó"), "aîpoba'e": ("medial_unseen", "aîpó"),
    # Distal (a'e also productive as ordinary third-person personal pronoun)
    "a'e": ("distal_unseen", "a'e"), "a'ea": ("distal_unseen", "a'e"),
    "a'eba'e": ("distal_unseen", "a'e"),
    "akó": ("distal_unseen", "akó"), "akoa": ("distal_unseen", "akó"),
    "akoba'e": ("distal_unseen", "akó"), "akûé": ("distal_unseen", "akûeî"),
    "akûeî": ("distal_unseen", "akûeî"), "akûeîa": ("distal_unseen", "akûeî"),
    "akûeîba'e": ("distal_unseen", "akûeî"),
    "kûé": ("distal_visible", "kûeî"), "kûeî": ("distal_visible", "kûeî"),
    "kûeîa": ("distal_visible", "kûeî"), "kûeîba'e": ("distal_visible", "kûeî"),
}

# Related material inventoried separately: no automatic inclusion in nominal
# deictic/copular totals. aé = intensifier 'same'; é = truth/assertive,
# niã = presentational particle; ahẽ = human 3rd-person demonstrative/pronoun.
RELATED = {
    "aé": ("demonstrative_reinforcer", "aé"),
    "ahẽ": ("human_demonstrative_or_pronoun", "ahẽ"),
    "aõa": ("demonstrative_reinforcer", "aõa"),
    "erika": ("demonstrative_reinforcer", "erika"),
    "niã": ("presentational_particle", "niã"),
    "é": ("assertive_particle", "é"),
    "a'ereme": ("derived_anaphoric_connective", "a'ereme"),
    "ãgûa": ("uncertain_pronominal", "ãgûa"),
}

# Unicode alpha and internal apostrophes; no stems or strings inside words.
TOKEN = re.compile(r"(?u)[^\W\d_]+(?:['’][^\W\d_]+)*")

def forms_in_text(text: str, *, letter=0, line_id="", tupi_context="", portuguese_context=""):
    tokens = list(TOKEN.finditer(text))
    results = []
    for pos, match in enumerate(tokens):
        surface = match.group()
        key = surface.casefold().replace("’", "'").replace("‘", "'")
        if key in FORMS:
            family, lemma = FORMS[key]
            inventory = "core"
        elif key in RELATED:
            family, lemma = RELATED[key]
            inventory = "related"
        else:
            continue
        previous = (tokens[pos - 1].group().casefold() if pos else "").replace("’", "'")
        following = (tokens[pos + 1].group().casefold() if pos + 1 < len(tokens) else "").replace("’", "'")
        # Identical form ang(a) may be the lexical noun 'soul' rather than
        # the proximal demonstrative. Preserve the hit for audit but exclude.
        if key == "anga" and (
                re.search(r"\balma\b", portuguese_context, re.IGNORECASE)
                or previous in ("xe", "nde", "pe", "oré", "îandé", "yandé")
                or "'anga" in text.casefold().replace("’", "'")):
            role = "excluded_homograph_soul"
            inventory = "excluded"
        elif key == "a'e":
            role = "third_person_pronoun_or_distal_demonstrative_unresolved"
        elif key == "ã":
            role = "presentative_temporal_or_deictic_unresolved"
        elif key in ("kó", "ikó") and following in ("ixé", "oroîur", "oroîkó", "aîkó"):
            role = "presentative_or_clausal_deictic"
        elif key in ("kó", "ikó"):
            role = "nominal_determiner_or_pronominal_deictic"
        elif key in ("aîpó", "koba'e", "kóba'e", "akûeîba'e"):
            role = "anaphoric_determiner_or_independent_pronoun"
        elif key in RELATED:
            role = "related_not_automatically_nominal_demonstrative"
        else:
            role = "referential_deictic_role_unresolved"
        results.append({
            "hit_id": "",
            "line_id": line_id,
            "letter": letter,
            "surface": surface,
            "lemma": lemma,
            "family": family,
            "inventory_class": inventory,
            "provisional_function": role,
            "preceding_token": previous,
            "following_token": following,
            "char_start": match.start(),
            "char_end": match.end(),
            "tupi": tupi_context or text,
            "portuguese": portuguese_context,
            "clause_ids": "",
            "copular_context": "",
            "predication_interposition": "not_determined",
            "editorial_status": "needs_philological_review",
        })
    return results

def augment(rows: list[dict], clauses: list[dict]):
    by_id = {row["id"]: row for row in rows}
    all_hits = []
    for row in rows:
        matches = forms_in_text(row["tupi"], letter=row["letter"], line_id=row["id"],
                                tupi_context=row["tupi"], portuguese_context=row["portuguese"])
        for match in matches:
            match["hit_id"] = f"D{len(all_hits)+1:04d}"
            match["clause_ids"] = row.get("clause_ids", "")
            match["copular_context"] = row.get("predication_kind", "")
            clause_ids = set(row.get("clause_ids", "").split(";"))
            if match["surface"].casefold() == "ã" and any(
                c["id"] in clause_ids and c["strategy"] == "deictic_between" for c in clauses
            ):
                match["predication_interposition"] = "between_nominal_constituents"
                match["provisional_function"] = "interposed_presentative_deictic_candidate"
            elif clause_ids and match["inventory_class"] == "core":
                match["predication_interposition"] = "in_predication_span_role_unresolved"
        strict = [match for match in matches if match["inventory_class"] == "core"]
        related = [match for match in matches if match["inventory_class"] == "related"]
        row["demonstrative_candidates"] = ";".join(m["surface"] for m in strict)
        row["demonstrative_lemmas"] = ";".join(m["lemma"] for m in strict)
        row["demonstrative_candidate_count"] = len(strict)
        row["has_demonstrative_candidate"] = bool(strict)
        row["related_deictic_particle_candidates"] = ";".join(m["surface"] for m in related)
        row["demonstrative_hit_ids"] = ";".join(m["hit_id"] for m in matches)
        all_hits.extend(matches)
    by_line = defaultdict(list)
    for match in all_hits:
        by_line[match["line_id"]].append(match)
    for clause in clauses:
        start = by_id[clause["start_id"]]
        end = by_id[clause["end_id"]]
        letter = start["letter"]
        clause_rows = [r for r in rows if r["letter"]==letter and start["line"]<=r["line"]<=end["line"]]
        clauses_hits = [hit for row in clause_rows for hit in by_line.get(row["id"],[]) if hit["inventory_class"] == "core"]
        clause["demonstrative_candidates"] = ";".join(m["surface"] for m in clauses_hits)
        clause["demonstrative_lemmas"] = ";".join(m["lemma"] for m in clauses_hits)
        clause["demonstrative_candidate_count"] = len(clauses_hits)
        clause["has_demonstrative_candidate"] = bool(clauses_hits)
        clause["demonstrative_roles_unreviewed"] = ";".join(m["provisional_function"] for m in clauses_hits)
        clause["contains_related_particles"] = ";".join(
            m["surface"] for row in clause_rows for m in by_line.get(row["id"],[]) if m["inventory_class"] == "related")
        if clause["strategy"] == "deictic_between":
            clause["demonstrative_predication_role"] = "candidate_interposed_deictic"
        elif clauses_hits:
            clause["demonstrative_predication_role"] = "in_predication_span_not_necessarily_copular"
        else:
            clause["demonstrative_predication_role"] = "none_detected_in_span"
    core = [hit for hit in all_hits if hit["inventory_class"]=="core"]
    related = [hit for hit in all_hits if hit["inventory_class"]=="related"]
    excluded = [hit for hit in all_hits if hit["inventory_class"]=="excluded"]
    predicated = [c for c in clauses if c["has_demonstrative_candidate"]]
    nominal = [c for c in clauses if c["kind"]=="nominal"]
    per_letter = {
        str(letter): {
            "core_hits": sum(x["letter"] == letter for x in core),
            "core_hit_lines": len({x["line_id"] for x in core if x["letter"] == letter}),
            "nominal_predicative_candidates_with_core_demo": sum(
                c["letter"] == letter and c["has_demonstrative_candidate"] for c in nominal),
        }
        for letter in range(1,7)
    }
    summary = {
        "definition": "Exact-token inclusive lexical search; no grammatical claim that each match is a copula.",
        "core_demo_token_hits": len(core),
        "core_demo_lines": len({x["line_id"] for x in core}),
        "related_particle_hits": len(related),
        "excluded_homograph_hits": len(excluded),
        "by_surface_core": dict(Counter(x["surface"].casefold() for x in core)),
        "by_lemma_core": dict(Counter(x["lemma"] for x in core)),
        "by_family_core": dict(Counter(x["family"] for x in core)),
        "related_by_form": dict(Counter(x["lemma"] for x in related)),
        "copular_candidates_with_core_demonstrative": len(predicated),
        "nominal_predication_candidates_with_core_demonstrative": sum(c["has_demonstrative_candidate"] for c in nominal),
        "original_zero_strategy_clauses_containing_core_demonstrative": sum(
            c["strategy"]=="zero" and c["has_demonstrative_candidate"] for c in clauses),
        "nominal_zero_strategy_clauses_containing_core_demonstrative": sum(
            c["strategy"]=="zero" and c["kind"]=="nominal" and c["has_demonstrative_candidate"] for c in clauses),
        "by_letter": per_letter,
        "remaining_ambiguity": "A'e is often third-person pronoun; kó/ikó often nominal determination; ã often presentative/temporal; é and niã not included as core demonstratives. All hits need syntactic review."
    }
    return all_hits, summary
