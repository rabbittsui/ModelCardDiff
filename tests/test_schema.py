"""Tests for the schema parser and required section resolution."""

import os
import unittest

from modelcarddiff import card, schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


class SchemaTests(unittest.TestCase):
    def test_parse_requires(self):
        parsed = schema.parse("require Overview\nrequire Results\n")
        self.assertEqual(parsed.required_sections, ("Overview", "Results"))

    def test_comments_and_blanks_ignored(self):
        parsed = schema.parse("# a comment\n\nrequire Overview\n")
        self.assertEqual(parsed.required_sections, ("Overview",))

    def test_duplicate_require_collapsed(self):
        parsed = schema.parse("require Overview\nrequire overview\n")
        self.assertEqual(parsed.required_sections, ("Overview",))

    def test_unknown_directive_raises(self):
        with self.assertRaises(schema.SchemaError):
            schema.parse("allow Overview\n")

    def test_require_without_name_raises(self):
        with self.assertRaises(schema.SchemaError):
            schema.parse("require\n")

