from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import compendio_bettendorf as cb


BETTENDORF_GROUND_TRUTH = """Santa Cruzra'angaba resé orépysyrõ îepé Tupã oré îar oréamotare'ymbara suí.

tuba ta'yra Espírito Santo rera pupé.

amém Jesus.

oré rub ybakype tekoar imoetepyramo toîkó nde rera.

tour nde Reino.

toîemonhang nde remimotara ybype ybakype i îemonhanga îabé.

oré rembi'u 'ara îabi'õndûara eîme'eng kori orébo.

ndenhyrõ oré angaîpaba resé orébo orérerekomemûãsara supé orénhyrõ îabé.

orémo'arukar umẽ îepé tentação pupé.

orépysyrõte îepé mba'eaíba suí.

amém Jesus.

Ave Maria graça resé tynysemba'e.

nde irũnamo îandé îara rekóû.

imombe'ukatupyramo ereikó kunhã suí.

imombe'ukatupyra abé nde membyra Jesus.

Santa Maria Tupã sy etupãmongetá oré iangaîpaba'e resé ko'yr irã oré îekyî oré rúmebéno.

amém Jesus.

Salva Rainha moraûsubara sy tekobé se'ẽba'e oré îerobîasaba salve.

endébo orosapukapukaî ipe'apyramo Eva membyramo.

endébo oronhe'angerur orépoasemamo oroîasegûabo ikó ybytygûaîa îase'ûaba pupé.

ene'ĩ oré resé îeruresar.

eboûing nde resaporaûsubara erobak oré koty.

a'e Jesus imombe'ukatupyra nde membyra ikó îepe'asagûera sykiré esepîakukar orébo.

nherane'ym poreaûsuberekoar se'ẽba'e Virgem Maria.

Santa Maria Tupã sy toréangaturam ne Christo remienõîûera resé oré îekosupagûama ri.

amém Jesus.

arobîar Tupã tuba opakatu mba'e tetiruã monhanga e'ikatuba'e ybaka yby abémonhangara.

arobîar JesusChrixtoabé ta'yra oîepeba'e asé îara.

Espírito Santo imonhangápe pitangĩnamo oîemonhangyba'epûera.

a'eba'e o'ar Maria ababykagûere'yma suí.

Poncio Pilato morubixabamo sekóreme serekomemûãmbyramo sekóû.

ybyraîoasaba resé imoîarypyramo sekóû iîukapyramo itymymbyramo sekóû.

ogûeîyb yby apyterype.

'ara mosapyra pupé omanõba'epûera suí sekobeîebyri.

oîeupir ybakype.

Tupã tuba opakatu mba'e tetiruã monhanga e'ikatuba'e 'ekatuaba koty seni.

a'e suí turi oîkobeba'e omanõba'epûera pabẽ rekomonhanga ne."""


@dataclass(frozen=True)
class CompendioCase:
    name: str
    ground_truth: str
    expressions: Sequence[object]
    allow_extra_lines: bool = True


def _normalize_expected_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped[-1] in ".;:!?":
            stripped = stripped[:-1]
        lines.append(stripped)
    return lines


def _render_lines(expressions: Iterable[object]) -> list[str]:
    return [expr.eval().strip() for expr in expressions]


CASES = [
    CompendioCase(
        name="bettendorff_compendio_pt_1",
        ground_truth=BETTENDORF_GROUND_TRUTH,
        expressions=cb.bettendorff_compendio_pt_1,
        allow_extra_lines=True,
    ),
]


class TestCompendioBettendorf(unittest.TestCase):
    def test_ground_truth_alignment(self) -> None:
        for case in CASES:
            with self.subTest(case=case.name):
                expected_lines = _normalize_expected_lines(case.ground_truth)
                actual_lines = _render_lines(case.expressions)
                if case.allow_extra_lines:
                    self.assertGreaterEqual(
                        len(actual_lines),
                        len(expected_lines),
                        msg=(
                            f"{case.name} line count mismatch: "
                            f"expected at least {len(expected_lines)} got {len(actual_lines)}"
                        ),
                    )
                else:
                    self.assertEqual(
                        len(actual_lines),
                        len(expected_lines),
                        msg=(
                            f"{case.name} line count mismatch: "
                            f"expected {len(expected_lines)} got {len(actual_lines)}"
                        ),
                    )
                for line_no, (actual, expected) in enumerate(
                    zip(actual_lines, expected_lines), start=1
                ):
                    with self.subTest(case=case.name, line=line_no):
                        self.assertEqual(
                            actual,
                            expected,
                            msg=(
                                f"{case.name} line {line_no} mismatch:\n"
                                f"expected: {expected}\n"
                                f"actual:   {actual}"
                            ),
                        )


if __name__ == "__main__":
    unittest.main()
