from __future__ import annotations

import unittest

from historic.lexicon import Noun, saba, v


class DeverbalNegationTest(unittest.TestCase):
    def test_negated_saba_adds_eym_suffix(self) -> None:
        marãtekó = Noun("marãtekó", definition="state of work, job, working")

        self.assertEqual((-(saba * v(marãtekó))).eval(), "marãtekoabe'yma")

    def test_saba_preserves_negated_verbalized_noun(self) -> None:
        marãtekó = Noun("marãtekó", definition="state of work, job, working")

        self.assertEqual((saba * -v(marãtekó)).eval(), "marãtekoabe'yma")


if __name__ == "__main__":
    unittest.main()
