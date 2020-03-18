"""Tests for the gate decision."""

import os
import unittest

from modelcarddiff import card, gate, schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


def _load(name):
    return card.parse_file(os.path.join(SAMPLES, name))
