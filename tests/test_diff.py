"""Tests for the version diff and change classification."""

import os
import unittest

from modelcarddiff import card, diff

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


def _load(name):
    return card.parse_file(os.path.join(SAMPLES, name))


class DiffTests(unittest.TestCase):
    def setUp(self):
        self.old = _load("complete.card")
        self.new = _load("complete-v2.card")
        self.changes = diff.diff(self.old, self.new)

    def test_detects_added_claim(self):
        added = [c for c in self.changes if c.kind == diff.ADDED_CLAIM]
        self.assertEqual(len(added), 1)
        self.assertIn("escalation", added[0].detail)

    def test_detects_removed_limitation(self):
        removed = [c for c in self.changes if c.kind == diff.REMOVED_LIMITATION]
        self.assertEqual(len(removed), 1)
        self.assertIn("refund and billing", removed[0].detail)
        self.assertTrue(diff.has_removed_limitation(self.changes))

    def test_detects_metric_regression(self):
        regressions = [c for c in self.changes if c.kind == diff.METRIC_REGRESSION]
        details = " ".join(c.detail for c in regressions)
        self.assertIn("eval-intent-accuracy", details)
