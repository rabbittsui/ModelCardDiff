"""Tests for the version diff and change classification."""

import os
import unittest

from modelcarddiff import card, diff

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


def _load(name):
