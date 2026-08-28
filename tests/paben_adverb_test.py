import unittest

from historic.lexicon import bae, aîpo, ikobé, îub, manõ, paben, pûera


class PabenAdverbTest(unittest.TestCase):
    def test_preposed_paben_triggers_circumstantial(self) -> None:
        self.assertEqual((paben + (aîpo * îub)).eval(), "pabẽ aîpoba'e ruî")

    def test_postposed_paben_keeps_existing_surface(self) -> None:
        expr = (bae * ikobé) + (pûera * (bae * manõ)) + paben

        self.assertEqual(expr.eval(), "oîkobeba'e omanõba'epûera pabẽ")


if __name__ == "__main__":
    unittest.main()
