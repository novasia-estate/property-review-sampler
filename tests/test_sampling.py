import unittest
from property_review_sampler import select

def population():
    return [{"row_id":f"{i}-{lang}","property_id":str(i),"market":["KH","TH","ID"][i%3],"language":lang,"must_review":i==0} for i in range(12) for lang in ["ru","en"]]
class SamplingTests(unittest.TestCase):
    def test_group_atomicity(self):
        r=select(population(),7);self.assertEqual(len(r["selected_rows"]),6);self.assertEqual(r["unused_budget_rows"],1)
        self.assertTrue(all(g["rows"]==2 for g in r["selected_groups"]))
    def test_coverage(self):self.assertEqual(select(population(),6)["uncovered_strata"],[])
    def test_order_independent(self):self.assertEqual(select(population(),8),select(list(reversed(population())),8))
    def test_seed(self):self.assertNotEqual(select(population(),8,seed="a")["selected_groups"],select(population(),8,seed="b")["selected_groups"])
    def test_mandatory(self):self.assertIn("0",[g["group"] for g in select(population(),2)["selected_groups"]])
    def test_mandatory_overflow(self):
        with self.assertRaises(ValueError):select(population(),1)
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):select([population()[0]]*2,2)
    def test_missing_stratum(self):
        with self.assertRaises(ValueError):select([{"row_id":"x","property_id":"x"}],2)
    def test_empty(self):self.assertEqual(select([],0)["selected_rows"],[])
    def test_no_mutation(self):
        rs=population();before=repr(rs);select(rs,6);self.assertEqual(repr(rs),before)
    def test_invalid_budget(self):
        for b in [-1,True,1.5]:
            with self.assertRaises(ValueError):select([],b)
    def test_invalid_flag(self):
        row=population()[0];row["must_review"]="false"
        with self.assertRaises(ValueError):select([row],2)
