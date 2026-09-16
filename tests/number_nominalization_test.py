import runpy
import unittest
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1] / "historic" / "araujo_catecismo_1686.tu.py"
)


class NumberNominalizationTest(unittest.TestCase):
    def test_raw_number_can_be_nominalized_for_postposition(self):
        entries = runpy.run_path(str(SOURCE))
        nominal = entries["n"](entries["opakombó"])

        self.assertEqual(nominal.eval(), "opakombó")
        self.assertIn("[NUMBER:TEN][NOUN]", nominal.eval(True))
        self.assertEqual((entries["iabiõ"] * nominal).eval(), "opakombó îabi'õ")

    def test_araujo_record_80_keeps_number_adjuncts_in_order(self):
        records = runpy.run_path(str(SOURCE))["araujo_catecismo_1686"]
        rendered = records[79].eval()
        editor_target = "opakombó îabi'õ Tupã supé oîepé asé mba'e moîa'oka"

        self.assertEqual("".join(rendered.split()), "".join(editor_target.split()))
        self.assertLess(rendered.index("îabi'õ"), rendered.index("supé"))
        self.assertLess(rendered.index("supé"), rendered.index("oîepé"))


if __name__ == "__main__":
    unittest.main()
