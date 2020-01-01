"""End to end tests for the CLI, including exit codes."""

import io
import os
import unittest
from contextlib import redirect_stdout

from modelcarddiff import cli

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")


