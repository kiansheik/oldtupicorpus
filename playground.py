from __future__ import annotations

from itertools import islice
from pprint import pp

import historic.lexicon as historic_lexicon
import historic.primary_sources as historic_sources
import pydicate
import synthetic.primary_sources as synthetic_sources
import tupi
from tupi import Noun as TupiNoun, TupiAntigo, Verb as TupiVerb
from tupi.orth import ALT_ORTS


def _export_public(module) -> dict[str, object]:
    exported = {}
    for name in getattr(module, "__all__", []):
        exported[name] = getattr(module, name)
    return exported


lexicon = _export_public(historic_lexicon)
globals().update(lexicon)

historic_samples = _export_public(historic_sources)
globals().update(historic_samples)

synthetic_samples = _export_public(synthetic_sources)
globals().update(synthetic_samples)

samples = {}
samples.update(historic_samples)
samples.update(synthetic_samples)


def render(expressions) -> list[str]:
    if callable(expressions):
        expressions = expressions()
    return [expr.eval() for expr in expressions]


def preview(expressions, limit: int = 5) -> list[object]:
    if callable(expressions):
        expressions = expressions()
    return list(islice(expressions, limit))


def play_help() -> None:
    print("oldtupicorpus playground")
    print(
        "available modules: pydicate, tupi, historic_lexicon, historic_sources, synthetic_sources"
    )
    print(f"historic samples: {', '.join(sorted(historic_samples))}")
    print(f"synthetic samples: {', '.join(sorted(synthetic_samples))}")
    print("examples:")
    print("  bettendorff_compendio[0].eval()")
    print("  araujo_catecismo_1686[0].eval()")
    print("  preview(verb(), 3)")
    print("  render(preview(verb(), 3))")
    print("  TupiAntigo()")


if __name__ == "__main__":
    play_help()
