"""Tests for the card parser."""

import os
import unittest

from modelcarddiff import card

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


class ParseTests(unittest.TestCase):
