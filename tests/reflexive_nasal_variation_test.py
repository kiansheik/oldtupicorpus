import runpy
import unittest
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1] / "historic" / "araujo_catecismo_1686.tu.py"
)


class ReflexiveNasalVariationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = runpy.run_path(str(SOURCE))

    def test_bare_variants_are_explicit_pronouns(self):
        entries = self.entries

        self.assertEqual(entries["îe"].eval(), "îe")
        self.assertEqual(entries["îo"].eval(), "îo")
        self.assertEqual(entries["nhe"].variation_id, 1)
        self.assertEqual(entries["nho"].variation_id, 1)
        self.assertEqual(entries["nhe"].eval(), "nhe")
        self.assertEqual(entries["nho"].eval(), "nho")
        self.assertEqual(entries["nhe"].inflection(), "refl")
        self.assertEqual(entries["nho"].inflection(), "mut")

    def test_variants_flow_through_verbal_and_short_nominal_forms(self):
        entries = self.entries
        monhang = entries["monhang"]
        mombeu = entries["mombeu"]

        self.assertEqual((entries["nhe"] * monhang).eval(), "onhemonhang")
        self.assertEqual((entries["nho"] * monhang).eval(), "onhomonhang")
        self.assertEqual(
            (entries["ae"] * monhang * entries["nhe"]).base_nominal().eval(),
            "onhemonhanga",
        )
        self.assertEqual(
            (entries["nhe"] * mombeu).var(1).base_nominal().eval(),
            "nhemombe'u",
        )
        self.assertEqual(
            (entries["nho"] * mombeu).var(1).base_nominal().eval(),
            "nhomombe'u",
        )

    def test_default_forms_and_approved_source_stay_unchanged(self):
        entries = self.entries
        self.assertEqual((entries["îe"] * entries["monhang"]).eval(), "oîemonhang")
        self.assertEqual(
            (entries["îe"] * entries["mombeu"]).var(1).base_nominal().eval(),
            "îemombe'u",
        )
        self.assertEqual(
            entries["araujo_catecismo_1686"][76].eval(),
            "seîxu îabi'õ îemombe'u",
        )


if __name__ == "__main__":
    unittest.main()
