"""Tests for the schema parser and required section resolution."""

import os
import unittest

from modelcarddiff import card, schema

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")

