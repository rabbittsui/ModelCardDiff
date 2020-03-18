"""Tests for the gate decision."""

import os
import unittest

from modelcarddiff import card, gate, schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


def _load(name):
    return card.parse_file(os.path.join(SAMPLES, name))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.schema = schema.parse_file(os.path.join(SAMPLES, "schema.txt"))

    def test_complete_card_passes(self):
        result = gate.gate(_load("complete.card"), self.schema)
        self.assertTrue(result.passed)
        self.assertEqual(result.findings, [])
