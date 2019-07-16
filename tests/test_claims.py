"""Tests for citation resolution, metric quotes, and limitation distinctness."""

import os
import unittest

from modelcarddiff import card, claims

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")
