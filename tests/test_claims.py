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
