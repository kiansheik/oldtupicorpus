import unittest

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


if __name__ == "__main__":
    unittest.main()
