try:
    from .verb_helpers import object_pronouns, subject_pronouns, test_cases_map
except ImportError:  # allow running as a script: python3 synthetic/verb_generator.py
    import os
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from synthetic.verb_helpers import (  # type: ignore
        object_pronouns,
        subject_pronouns,
        test_cases_map,
    )
from pydicate.lang.tupilang import *
from pydicate.lang.tupilang.pos import *

try:
    from tqdm import tqdm
except ModuleNotFoundError:  # optional dependency

    def tqdm(iterable, **kwargs):
        return iterable


SUPPORTED_MODES = {"indicativo", "permissivo", "imperativo"}
SUBJECTS_BY_MODE = {
    modo: sorted({x[0] for x in test_cases_map[modo]}) for modo in SUPPORTED_MODES
}
TRANSITIVE_COUNT_BY_MODE = {
    modo: len(test_cases_map[modo]) * 2 * 4 for modo in SUPPORTED_MODES
}
INTRANSITIVE_COUNT_BY_MODE = {
    modo: len(SUBJECTS_BY_MODE[modo]) * 2 * 4 for modo in SUPPORTED_MODES
}

_ESTIMATED_COUNT: int | None = None


def conjugate_transitive(
    entry: Verb, subj_tense: str, modo: str, posto: str, obj_tense: str
) -> Verb:
    subj = subject_pronouns[subj_tense]
    obj = object_pronouns[obj_tense]
    v_prot = entry * subj
    v = (v_prot * obj) if posto == "postposto" else (obj * v_prot)
    return v if modo != "permissivo" else v.perm()


def conjugate_intransitive(entry: Verb, subj_tense: str, modo: str, posto: str) -> Verb:
    subj = subject_pronouns[subj_tense]
    v_prot = entry * subj
    v = v_prot if posto == "postposto" else (subj * entry)
    return v if modo != "permissivo" else v.perm()


def build_verbs():
    """
    Yield Pydicate expressions for synthetic verbs (streaming generator).
    """
    verbs = Verb.iter_db_entries()
    for verb in tqdm(verbs, desc="Processing verbs"):
        is_transitive = verb.verb.transitivo
        for modo, test_cases in test_cases_map.items():
            if modo not in SUPPORTED_MODES:
                continue
            if is_transitive:
                for posto in ("anteposto", "postposto"):
                    for subj, obj in test_cases:
                        try:
                            trans_res = conjugate_transitive(
                                verb, subj, modo, posto, obj
                            )
                            neg_trans_res = -trans_res
                            pro_drop_res = +trans_res
                            neg_pro_drop_res = +neg_trans_res
                            yield trans_res
                            yield neg_trans_res
                            yield pro_drop_res
                            yield neg_pro_drop_res
                        except Exception as e:
                            print(
                                f"\t({subj} -> {obj}):\tainda não desenvolvida",
                                e,
                            )
            else:
                subjects = sorted({x[0] for x in test_cases})
                for posto in ("anteposto", "postposto"):
                    for subj in subjects:
                        try:
                            intr_res = conjugate_intransitive(verb, subj, modo, posto)
                            neg_intr_res = -intr_res
                            pro_drop_res = +intr_res
                            neg_pro_drop_res = +neg_intr_res
                            yield intr_res
                            yield neg_intr_res
                            yield pro_drop_res
                            yield neg_pro_drop_res
                        except Exception as e:
                            print(
                                f"\t({subj}):\tainda não desenvolvida",
                                e,
                            )


def estimate_verb_count() -> int:
    global _ESTIMATED_COUNT
    if _ESTIMATED_COUNT is not None:
        return _ESTIMATED_COUNT
    transitive = 0
    intransitive = 0
    for verb in Verb.iter_db_entries():
        if verb.verb.transitivo:
            transitive += 1
        else:
            intransitive += 1
    per_transitive = sum(TRANSITIVE_COUNT_BY_MODE.values())
    per_intransitive = sum(INTRANSITIVE_COUNT_BY_MODE.values())
    _ESTIMATED_COUNT = transitive * per_transitive + intransitive * per_intransitive
    return _ESTIMATED_COUNT
