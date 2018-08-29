"""Claim to evaluation citation resolution and related checks.

This module answers four questions about a parsed card:

1. Which capability claims cite an evaluation, and does that evaluation exist in
   the Results section (citation resolution).
2. Which capability claims cite nothing (uncited claim detection).
3. Which claims quote a metric name or value that does not appear in any result
   (metric quote checking).
4. Which limitations are boilerplate duplicates of each other rather than
   distinct statements (limitation distinctness).

Each check returns plain dataclasses so the gate and the report can format the
findings without re-deriving them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .card import Card, Claim

# Numbers quoted in a claim. Each match records where it sits so we can look at
# the words just before it and decide whether it is a bound or an exact value.
_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

