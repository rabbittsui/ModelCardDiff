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

