import runpy
import unittest
from pathlib import Path

from historic.lexicon import apixara, aûsub, nde, og


class OgPluriformPrefixTest(unittest.TestCase):
    def test_og_occupies_the_prefix_position_of_a_pluriform_noun(self):
        form = og * apixara

        self.assertEqual(form.eval(), "oapixara")
        self.assertIn("[PRONOUN:MAIN_CLAUSE_SUBJECT:3p]apixar", form.eval(True))
        self.assertNotIn("[PLURIFORM_PREFIX:T:ABSOLUTE]", form.eval(True))

    def test_other_prefix_choices_remain(self):
        self.assertEqual(apixara.eval(), "tapixara")
        self.assertEqual((nde * apixara).eval(), "nde rapixara")

    def test_pluriform_verb_nominal_already_joins_og_to_the_stem(self):
        self.assertEqual((og * aûsub).base_nominal().eval(), "ogaûsuba")

    def test_araujo_record_74_keeps_its_source_expression(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "historic"
            / "araujo_catecismo_1686.tu.py"
        )
        records = runpy.run_path(str(source))["araujo_catecismo_1686"]

        self.assertEqual(
            records[73].eval(),
            "oîeaûsuba îabé asé oapixararaûsuba no",
        )


if __name__ == "__main__":
    unittest.main()
