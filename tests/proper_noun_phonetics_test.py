import unittest

from historic.lexicon import domingo, esé, noworkday
from pydicate.lang.tupilang.pos import Noun, Postposition, ProperNoun, Verb


class ProperNounPhoneticsTest(unittest.TestCase):
    def test_proper_noun_object_preserves_is(self):
        self.assertEqual((ProperNoun("missa") * Verb("endub")).eval(), "missa osendub")

    def test_non_proper_noun_still_uses_is_phonetic_rule(self):
        self.assertEqual((Noun("missa") * Verb("endub")).eval(), "mixsa osendub")

    def test_araujo_missa_line_preserves_proper_noun_surface(self):
        esebé = Postposition(
            "esebé", definition="(t) (posp.) - com, juntamente com, assim como"
        )
        missa = ProperNoun("missa", definition="mass")
        endub = Verb("endub")

        expr = (esé * domingo) + (esebé * noworkday) + (missa * endub)

        self.assertEqual(
            expr.eval(),
            "domingo resé 'ara marãtekoabe'yma resebé missarendubi",
        )

    def test_proper_noun_base_nominal_preserves_is(self):
        self.assertEqual(
            (ProperNoun("missa") * Verb("endub")).base_nominal().eval(),
            "missarenduba",
        )

    def test_non_proper_noun_base_nominal_still_uses_is_phonetic_rule(self):
        self.assertEqual(
            (Noun("missa") * Verb("endub")).base_nominal().eval(),
            "mixsarenduba",
        )

    def test_araujo_nominal_missa_line_preserves_proper_noun_surface(self):
        esebé = Postposition(
            "esebé", definition="(t) (posp.) - com, juntamente com, assim como"
        )
        missa = ProperNoun("missa", definition="mass")
        endub = Verb("endub")

        expr = (esé * domingo) + (esebé * noworkday) + (missa * endub).base_nominal()

        self.assertEqual(
            expr.eval(),
            "domingo resé 'ara marãtekoabe'yma resebé missarenduba",
        )


if __name__ == "__main__":
    unittest.main()
