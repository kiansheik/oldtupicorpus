import unittest

from historic.lexicon import ae, asé, aûsub, mbae, opakatu, tetiruã, îe, îo


class BaseNominalObjectProDropTest(unittest.TestCase):
    def test_non_pronoun_object_pro_drop_suppresses_surface_in_nominal_form(self):
        opkmbt = opakatu + (mbae + tetiruã)
        nominal = (asé * aûsub * +opkmbt).base_nominal()

        self.assertEqual(nominal.eval(), "asé saûsuba")
        self.assertEqual(nominal.arguments[1].eval(), "opakatu mba'e tetiruã")
        self.assertTrue(nominal.arguments[1].pro_drop)

    def test_pronoun_object_pro_drop_contrast_is_unchanged(self):
        self.assertEqual((asé * aûsub * +ae).base_nominal().eval(), "asé saûsuba")

    def test_third_person_reflexive_nominal_uses_correlational_prefix(self):
        self.assertEqual((+asé * aûsub * îe).base_nominal().eval(), "oîeaûsuba")

    def test_third_person_reciprocal_nominal_uses_correlational_prefix(self):
        self.assertEqual((+asé * aûsub * îo).base_nominal().eval(), "oîoaûsuba")


if __name__ == "__main__":
    unittest.main()
