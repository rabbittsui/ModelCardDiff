"""Tests for the schema parser and required section resolution."""

import os
import unittest

from modelcarddiff import card, schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


class SchemaTests(unittest.TestCase):
    def test_parse_requires(self):
        parsed = schema.parse("require Overview\nrequire Results\n")
        self.assertEqual(parsed.required_sections, ("Overview", "Results"))
