import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

from historic.lexicon import (
    béno,
    eme,
    endé,
    erekó,
    irã,
    ixé,
    oré,
    poî,
    tupãmongetá,
    îekyî,
    îub,
)


OBJECTS = [
    ("01-iekyl-independente", îekyî * +oré),
    ("02-iub-independente", îub * +oré),
    ("03-gerundio-posicional", (îekyî * +oré) << (îub * +oré)),
    ("04-temporal-simples", eme * (îekyî * ixé)),
    (
        "05-temporal-complexa",
        (+endé * tupãmongetá).imp() << (irã + ((îub * oré) >> (îekyî * oré)) << béno),
    ),
    (
        "06-auxiliar-derivado-ereko",
        (poî * ixé) << (erekó * ixé),
    ),
]


def main():
    for slug, obj in OBJECTS:
        forest, links = obj.to_forest_tree()
        payload = {
            "surface": obj.eval(),
            "annotated": obj.eval(annotated=True),
            "semantic": obj.semantic(),
            "translation_prompt": obj.translation_prompt("Portuguese"),
            "forest_tree": forest,
            "forest_links": links,
        }
        (HERE / f"{slug}.pydicate.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
