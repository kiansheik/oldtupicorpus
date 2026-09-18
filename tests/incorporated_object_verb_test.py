import runpy
import unittest
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1] / "historic" / "araujo_catecismo_1686.tu.py"
)


class IncorporatedObjectVerbTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = runpy.run_path(str(SOURCE))

    def test_default_is_intransitive_with_incorporated_generic_object(self):
        potaba = self.entries["potaba"]
        meeng = self.entries["meeng"]
        derived = potaba / meeng
        self.assertFalse(derived.verb.transitivo)
        self.assertEqual(derived.category, "incorporated_object_verb")
        self.assertEqual(derived.incorporated_object.verbete, "potaba")
        self.assertIn("[INCORPORATED_OBJECT]", derived.base_nominal().eval(True))
        self.assertIn(
            "[OBJECT:INCORPORATED:GENERIC]", derived.base_nominal().eval(True)
        )

    def test_variation_one_uses_external_object_as_noun_possessor(self):
        potaba = self.entries["potaba"]
        meeng = self.entries["meeng"]
        tupan = self.entries["tupan"]
        derived = (potaba / meeng).var(1)
        self.assertTrue(derived.verb.transitivo)
        applied = derived * tupan
        self.assertIsNone(applied.subject())
        self.assertEqual(applied.object().verbete, "Tupã")
        nominal = applied.base_nominal()
        self.assertEqual(nominal.eval(), "Tupã potame'enga")
        self.assertIn("[INCORPORATED_OBJECT]", nominal.eval(True))
        self.assertIn("[OBJECT:INCORPORATED:POSSESSED]", nominal.eval(True))
        self.assertIn("[OBJECT:DIRECT:INCORPORATED_NOUN_POSSESSOR]", nominal.eval(True))

        subject = self.entries["ixé"]
        two_args = derived * subject * tupan
        self.assertEqual(two_args.subject().verbete, subject.verbete)
        self.assertEqual(two_args.object().verbete, tupan.verbete)
        self.assertEqual(two_args.base_nominal().eval(), "ixé Tupã potame'enga")

    def test_historic_record_81_uses_the_possessor_variation(self):
        record = self.entries["araujo_catecismo_1686"][80]
        self.assertEqual(record.eval(), "oemitymbûerypy pupé Tupã potame'enga no")
        self.assertIn("[INCORPORATED_OBJECT]", record.eval(True))

    def test_existing_noun_compound_and_verb_object_are_unchanged(self):
        potaba = self.entries["potaba"]
        meeng = self.entries["meeng"]
        tupan = self.entries["tupan"]
        self.assertEqual(
            (tupan * (potaba / self.entries["ypy"])).eval(), "Tupã potabypy"
        )
        self.assertEqual((potaba * meeng).eval(), "motaba oîme'eng")


if __name__ == "__main__":
    unittest.main()
