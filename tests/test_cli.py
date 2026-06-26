"""End to end tests for the CLI, including exit codes."""

import io
import os
import unittest
from contextlib import redirect_stdout

from modelcarddiff import cli

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


def _run(argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = cli.main(argv)
    return code, out.getvalue()


class CliTests(unittest.TestCase):
    def test_gate_complete_exit_zero(self):
        code, out = _run(
            ["gate", os.path.join(SAMPLES, "schema.txt"), os.path.join(SAMPLES, "complete.card")]
        )
        self.assertEqual(code, 0)
        self.assertIn("PASS", out)

    def test_gate_incomplete_exit_one(self):
        code, out = _run(
            ["gate", os.path.join(SAMPLES, "schema.txt"), os.path.join(SAMPLES, "incomplete.card")]
        )
        self.assertEqual(code, 1)
        self.assertIn("REFUSE", out)

    def test_diff_regression_exit_one(self):
        code, out = _run(
            ["diff", os.path.join(SAMPLES, "complete.card"), os.path.join(SAMPLES, "complete-v2.card")]
        )
        self.assertEqual(code, 1)
        self.assertIn("removed limitation", out)
        self.assertIn("metric regression", out)

    def test_diff_identical_exit_zero(self):
        code, out = _run(
            ["diff", os.path.join(SAMPLES, "complete.card"), os.path.join(SAMPLES, "complete.card")]
        )
        self.assertEqual(code, 0)

    def test_claims_exit_zero(self):
        code, out = _run(["claims", os.path.join(SAMPLES, "complete.card")])
        self.assertEqual(code, 0)
        self.assertIn("CITES", out)

    def test_claims_incomplete_shows_uncited(self):
        code, out = _run(["claims", os.path.join(SAMPLES, "incomplete.card")])
        self.assertEqual(code, 0)
        self.assertIn("UNCITED", out)
        self.assertIn("DANGLING", out)

    def test_version(self):
        code, out = _run(["version"])
        self.assertEqual(code, 0)
        self.assertIn("modelcarddiff", out)


if __name__ == "__main__":
    unittest.main()
