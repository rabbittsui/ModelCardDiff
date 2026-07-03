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

    def test_resolve_missing_and_present(self):
        sch = schema.parse("require Overview\nrequire Limitations\n")
        parsed = card.parse("## Overview\n\nbody\n")
        statuses = schema.resolve_sections(sch, parsed)
        by_name = {s.name: s for s in statuses}
        self.assertTrue(by_name["Overview"].satisfied)
        self.assertFalse(by_name["Limitations"].present)

    def test_resolve_empty_section_not_satisfied(self):
        sch = schema.parse("require Overview\n")
        parsed = card.parse("## Overview\n\n\n")
        status = schema.resolve_sections(sch, parsed)[0]
        self.assertTrue(status.present)
        self.assertFalse(status.non_empty)
        self.assertFalse(status.satisfied)

    def test_parse_sample_schema(self):
        sch = schema.parse_file(os.path.join(SAMPLES, "schema.txt"))
        self.assertEqual(len(sch.required_sections), 5)


if __name__ == "__main__":
    unittest.main()
