from __future__ import annotations

import unittest

from historic.lexicon import Verb, moro, nde, pysyro, saba, sara


class MoroIncorporationTest(unittest.TestCase):
    def test_moro_absolute_remains_moro(self) -> None:
        self.assertEqual(moro.eval(), "moro")

    def test_moro_incorporates_as_poro_in_conjugated_verb(self) -> None:
        apiti = Verb("apiti", definition="murder")

        self.assertEqual((+nde * apiti * moro).imp().eval(), "eporoapiti")
        self.assertEqual((-(+nde * apiti * moro).imp()).eval(), "eporoapiti umẽ")

    def test_moro_stays_absolute_in_deverbal_forms(self) -> None:
        apiti = Verb("apiti", definition="murder")

        self.assertEqual((sara.var(1) * (moro * pysyro)).eval(), "moropysyrõana")
        self.assertEqual((nde * (saba * (apiti * moro))).eval(), "nde moroapitîaba")


if __name__ == "__main__":
    unittest.main()
