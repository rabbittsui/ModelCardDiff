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
