"""Regression tests: lexical demonstrative candidate extraction is not a copula parser."""
import unittest
from demonstratives import forms_in_text, augment

def core(tupi, translation=""):
    return [x["lemma"] for x in forms_in_text(tupi, portuguese_context=translation) if x["inventory_class"]=="core"]

class DemonstrativeTests(unittest.TestCase):
    def test_core_forms(self):
        self.assertEqual(core("Kó xe nhe’enga. Koba’e tekó."), ["kó","kó"])
        self.assertEqual(core("Nde ruba é ã ixé."), ["ã"])
        self.assertEqual(core("Aîpó nhõ, ebokûé koty, akûeîba’e rekó."), ["aîpó","ebokûé","akûeî"])
    def test_ambiguity(self):
        match=forms_in_text("A’e abé oîme’ẽ.")
        self.assertEqual(match[0]["provisional_function"],"third_person_pronoun_or_distal_demonstrative_unresolved")
    def test_no_prefix_substring_or_soul(self):
        self.assertEqual(core("aîkó nde ‘anga n’a’ekatúi.", "estou tua alma"), [])
        self.assertEqual(core("orérekó"), [])
    def test_separate_particles(self):
        self.assertEqual(core("É niã aé ahẽ a’ereme"), [])
        self.assertTrue(all(x["inventory_class"]=="related" for x in forms_in_text("É niã aé ahẽ a’ereme")))
    def test_zero_copula_not_zero_demonstrative(self):
        rows=[{"id":"C01-L001","letter":1,"line":1,"tupi":"Koba’e tekó","portuguese":"Esta ação","clause_ids":"P001","predication_kind":"nominal"},
              {"id":"C01-L002","letter":1,"line":2,"tupi":"ma’egûasueté","portuguese":"é algo grande","clause_ids":"P001","predication_kind":"nominal"}]
        clauses=[{"id":"P001","letter":1,"start_id":"C01-L001","end_id":"C01-L002","strategy":"zero","kind":"nominal"}]
        hits, summary=augment(rows,clauses)
        self.assertEqual(len(hits),1)
        self.assertTrue(clauses[0]["has_demonstrative_candidate"])
        self.assertEqual(summary["nominal_zero_strategy_clauses_containing_core_demonstrative"],1)

if __name__=="__main__":
    unittest.main()
