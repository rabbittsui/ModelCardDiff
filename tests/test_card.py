"""Tests for the card parser."""

import os
import unittest

from modelcarddiff import card

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


class ParseTests(unittest.TestCase):
    def test_title_and_sections(self):
        text = "# Model Card: x\n\n## Overview\n\nbody\n\n## Results\n\nid = m 1\n"
        parsed = card.parse(text)
        self.assertEqual(parsed.title, "Model Card: x")
        self.assertIsNotNone(parsed.section("Overview"))
        self.assertIsNotNone(parsed.section("results"))
        self.assertIsNone(parsed.section("Missing"))

    def test_claim_with_citation(self):
        text = (
