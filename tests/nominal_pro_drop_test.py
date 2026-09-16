from __future__ import annotations

import unittest

from historic.lexicon import ae, gûeîyb, ikobé, jesus, saguera


class NominalProDropTest(unittest.TestCase):
    def test_displaced_proper_noun_keeps_third_person_nominal_prefix(self) -> None:
        self.assertEqual((saguera(jesus * ikobé)).eval(), "Jesus rekobesagûera")
        self.assertEqual((saguera(+jesus * ikobé)).eval(), "sekobesagûera")

    def test_displaced_pronoun_precedent_still_keeps_third_person_prefix(self) -> None:
        self.assertEqual((saguera(+ae * ikobé)).eval(), "sekobesagûera")
        self.assertEqual((saguera(+ae * gûeîyb)).eval(), "i gûeîybagûera")


if __name__ == "__main__":
    unittest.main()
