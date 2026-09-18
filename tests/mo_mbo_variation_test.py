import runpy
import unittest
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1] / "historic" / "araujo_catecismo_1686.tu.py"
)


class MoMboVariationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = runpy.run_path(str(SOURCE))

    def test_mbo_is_variation_one_of_mo(self):
        mo = self.entries["mo"]
        mbo = self.entries["mbo"]

        self.assertEqual(mo.eval(), "mo")
        self.assertEqual(mbo.variation_id, 1)
        self.assertEqual(mbo.eval(), "mbo")
        self.assertEqual((mbo * self.entries["îasuk"]).eval(), "mboîasuk")
        self.assertIn(
            "mbo[CAUSATIVE_PREFIX:MBO]îasuk",
            (mbo * self.entries["îasuk"]).eval(True),
        )

    def test_approved_mo_contrasts_remain(self):
        entries = self.entries
        records = entries["araujo_catecismo_1686"]

        self.assertEqual((entries["mo"] * entries["îaok"]).eval(), "moîa'ok")
        self.assertEqual(records[39].eval(), "arobîar Santos rekokatu îemoîa'oîa'oka")
        self.assertEqual(
            records[79].eval(),
            "opakombó îabi'õ Tupã supé oîepé asé mba'emoîa'oka",
        )

    def test_araujo_record_82_uses_explicit_mbo(self):
        record = self.entries["araujo_catecismo_1686"][81]
        target = "i karaíba pupé îemboîasuka"

        self.assertEqual("".join(record.eval().split()), "".join(target.split()))


if __name__ == "__main__":
    unittest.main()
