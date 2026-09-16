import runpy
import unittest
from pathlib import Path

from historic.lexicon import iabiõ, mombeu, îe, îo
from pydicate.lang.tupilang.pos import Noun


class ReflexiveNominalVariationTest(unittest.TestCase):
    def test_reflexive_base_nominal_default_keeps_correlational_form(self):
        self.assertEqual((îe * mombeu).base_nominal().eval(), "oîo mombe'u")

    def test_reflexive_base_nominal_variant_uses_short_prefix(self):
        self.assertEqual((îe * mombeu).var(1).base_nominal().eval(), "îemombe'u")

    def test_reciprocal_base_nominal_variant_uses_short_prefix(self):
        self.assertEqual((îo * mombeu).var(1).base_nominal().eval(), "îomombe'u")

    def test_araujo_annual_confession_phrase_variant(self):
        seîxu = Noun("seîxu", "ano")

        expr = (iabiõ * seîxu) + (îe * mombeu).var(1).base_nominal()

        self.assertEqual(expr.eval(), "seîxu îabi'õ îemombe'u")

    def test_transitive_with_only_reflexive_or_reciprocal_object(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "historic"
            / "araujo_catecismo_1686.tu.py"
        )
        entries = runpy.run_path(str(source))
        kuakub = entries["kuakub"]
        smi = entries["smi"]
        reflexive = entries["îe"] * kuakub
        reciprocal = entries["îo"] * kuakub

        self.assertTrue(kuakub.verb.transitivo)
        self.assertEqual(reflexive.base_nominal().eval(), "oîekuakuba")
        self.assertEqual(reflexive.var(1).base_nominal().eval(), "îekuakuba")
        self.assertEqual(reciprocal.base_nominal().eval(), "oîokuakuba")
        self.assertEqual(reciprocal.var(1).base_nominal().eval(), "îokuakuba")
        self.assertEqual(
            (smi * kuakub * entries["îe"]).var(1).base_nominal().eval(),
            "Santa Madre Igreja îekuakuba",
        )

    def test_araujo_fast_nominal_uses_editor_authored_expression(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "historic"
            / "araujo_catecismo_1686.tu.py"
        )
        records = runpy.run_path(str(source))["araujo_catecismo_1686"]

        self.assertEqual(
            records[78].eval(),
            "Santa Madre Igreja îekuakupûaîa îabi'õ îekuakuba",
        )


if __name__ == "__main__":
    unittest.main()
