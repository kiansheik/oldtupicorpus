import unittest

from historic.lexicon import emi, nde, og, tym


class EmiReferentialTest(unittest.TestCase):
    def test_nasal_stem_keeps_emi_prefix(self):
        absolute = emi * tym

        self.assertEqual(absolute.eval(), "temityma")
        self.assertIn("emi[PATIENT_PREFIX]tym", absolute.eval(True))

    def test_referential_pronoun_occupies_prefix_position(self):
        referential = og * (emi * tym)

        self.assertEqual(referential.eval(), "oemityma")
        self.assertIn(
            "o[PRONOUN:MAIN_CLAUSE_SUBJECT:3p]emi[PATIENT_PREFIX]tym",
            referential.eval(True),
        )
        self.assertNotIn("[PLURIFORM_PREFIX:T:ABSOLUTE]", referential.eval(True))

    def test_ordinary_possessor_keeps_relative_prefix(self):
        self.assertEqual((nde * (emi * tym)).eval(), "nde remityma")


if __name__ == "__main__":
    unittest.main()
