import runpy
import unittest
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1] / "historic" / "araujo_catecismo_1686.tu.py"
)


class MPluriformPossessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = runpy.run_path(str(SOURCE))

    def test_m_noun_uses_m_absolute_and_p_possessed(self):
        potaba = self.entries["potaba"]
        tupapotaba = self.entries["tupapotaba"]

        self.assertEqual(potaba.eval(), "motaba")
        self.assertEqual((self.entries["nde"] * potaba).eval(), "nde potaba")
        self.assertEqual(tupapotaba.eval(), "Tupã potaba")
        self.assertIn("p[PLURIFORM_PREFIX:P]otab", tupapotaba.eval(True))
        self.assertEqual((potaba * self.entries["meeng"]).eval(), "motaba oîme'eng")

    def test_araujo_record_81_keeps_p_as_incorporated_possessed_noun(self):
        record = self.entries["araujo_catecismo_1686"][80]
        target = "oemitymbûerypy pupé Tupã potame'enga no"

        self.assertEqual("".join(record.eval().split()), "".join(target.split()))
        self.assertIn(
            "p[PLURIFORM_PREFIX:P]ota[INCORPORATED_OBJECT]", record.eval(True)
        )
        self.assertIn("[OBJECT:DIRECT:INCORPORATED_NOUN_POSSESSOR]", record.eval(True))

    def test_t_class_keeps_r_when_possessed(self):
        self.assertEqual(
            (self.entries["nde"] * self.entries["apixara"]).eval(),
            "nde rapixara",
        )


if __name__ == "__main__":
    unittest.main()
