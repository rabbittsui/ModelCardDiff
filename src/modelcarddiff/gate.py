"""The pass or refuse decision.

The gate runs four checks against a card and a schema:

1. Every required section exists and is non-empty.
2. Every capability claim cites an evaluation (no uncited claims), and every
   cited evaluation exists in the results (no dangling citations).
3. Every quoted metric value appears in the results (no claim quotes a metric
   absent from the results).
4. Every stated limitation is distinct (no boilerplate duplicates).

The gate returns a :class:`GateResult` carrying the ordered list of findings.
The decision is ``passed`` when there are no findings. Findings are produced in
a fixed order so identical input yields byte-identical output.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import claims as claims_mod
from .card import Card
from .schema import Schema, resolve_sections

# Finding codes. Stable identifiers so reports and tests can refer to them.
MISSING_SECTION = "missing-section"
EMPTY_SECTION = "empty-section"
UNCITED_CLAIM = "uncited-claim"
DANGLING_CITATION = "dangling-citation"
UNMATCHED_METRIC = "unmatched-metric"
DUPLICATE_LIMITATION = "duplicate-limitation"


@dataclass(frozen=True)
class Finding:
    """A single reason the gate refuses.

    code is one of the stable finding codes above.
    message is a human readable one line explanation.
    line is the 1 based source line when known, else 0.
    """

    code: str
    message: str
    line: int = 0


@dataclass
class GateResult:
