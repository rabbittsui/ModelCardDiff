"""Tests for citation resolution, metric quotes, and limitation distinctness."""

import os
import unittest

from modelcarddiff import card, claims

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


class CitationTests(unittest.TestCase):
    def test_resolved_citation(self):
        parsed = card.parse(
            "## Capabilities\n- claim: t (cites: e)\n## Results\ne = m 1\n"
        )
        cites = claims.resolve_citations(parsed)
        self.assertTrue(cites[0].resolved)
        self.assertFalse(cites[0].uncited)
        self.assertFalse(cites[0].dangling)

    def test_uncited_claim(self):
        parsed = card.parse("## Capabilities\n- claim: no reference here\n")
        self.assertEqual(len(claims.uncited_claims(parsed)), 1)

    def test_dangling_citation(self):
        parsed = card.parse(
            "## Capabilities\n- claim: t (cites: missing)\n## Results\ne = m 1\n"
        )
        dangling = claims.dangling_claims(parsed)
        self.assertEqual(len(dangling), 1)
        self.assertEqual(dangling[0].cited_id, "missing")


class MetricQuoteTests(unittest.TestCase):
    def test_bound_phrasing_not_flagged(self):
        parsed = card.parse(
            "## Capabilities\n- claim: accuracy above 0.99 (cites: e)\n"
            "## Results\ne = accuracy 0.9\n"
        )
        self.assertEqual(claims.unmatched_metric_quotes(parsed), [])

    def test_exact_value_present(self):
        parsed = card.parse(
            "## Capabilities\n- claim: accuracy of 0.9 (cites: e)\n"
            "## Results\ne = accuracy 0.9\n"
        )
        self.assertEqual(claims.unmatched_metric_quotes(parsed), [])

    def test_exact_value_absent(self):
        parsed = card.parse(
            "## Capabilities\n- claim: accuracy of 0.99 (cites: e)\n"
            "## Results\ne = accuracy 0.9\n"
        )
        unmatched = claims.unmatched_metric_quotes(parsed)
        self.assertEqual(len(unmatched), 1)
        self.assertEqual(unmatched[0].quoted, "0.99")

    def test_uncited_claim_not_metric_checked(self):
        parsed = card.parse("## Capabilities\n- claim: accuracy of 0.99\n")
        self.assertEqual(claims.unmatched_metric_quotes(parsed), [])


class DistinctLimitationTests(unittest.TestCase):
    def test_distinct_limitations_no_duplicates(self):
        parsed = card.parse(
            "## Limitations\n- English only input\n- truncates long messages\n"
        )
