import copy, unittest
from property_review_sampler import select
from test_sampling import population

class ReviewScopeTests(unittest.TestCase):
    def test_whole_groups_excluded_and_reasons_retained(self):
        rows=population();r=select(rows,24,exclude_groups={"1":"Reviewed in batch A"})
        self.assertFalse(any(x["property_id"]=="1" for x in r["selected_rows"]))
        self.assertEqual(r["excluded_groups"],[{"group":"1","reason":"Reviewed in batch A","row_ids":["1-en","1-ru"]}])
        self.assertEqual((r["population_rows"],r["eligible_rows"],r["schema_version"]),(24,22,2))
    def test_mandatory_conflict_is_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError,"mandatory"):select(population(),8,exclude_groups={"0":"Reviewed"})
    def test_unknown_ids_and_invalid_reasons_rejected(self):
        for value in [{"absent":"Reviewed"},{"1":" "},{"1":None},{"1":"x"*501},["1"],False]:
            with self.subTest(value=value),self.assertRaises(ValueError):select(population(),8,exclude_groups=value)
    def test_no_mutation_order_independence_and_fingerprint(self):
        rows=population();policy={"1":"Checked"};before=copy.deepcopy((rows,policy));r=select(rows,6,exclude_groups=policy)
        self.assertEqual((rows,policy),before);self.assertEqual(r,select(rows[::-1],6,exclude_groups=policy));self.assertEqual(r["population_sha256"],select(rows,6)["population_sha256"])
    def test_excluded_strata_do_not_claim_eligible_coverage(self):
        rows=[{"row_id":"a","property_id":"a","market":"KH","language":"ru"},{"row_id":"b","property_id":"b","market":"TH","language":"en"}]
        r=select(rows,0,exclude_groups={"a":"Checked"});self.assertEqual(r["uncovered_strata"],[{"market":"TH","language":"en"}]);self.assertEqual(len(r["excluded_groups"]),1)
    def test_legacy_shape_unchanged_without_policy(self):
        r=select(population(),6);self.assertEqual(r["schema_version"],1);self.assertNotIn("excluded_groups",r)
