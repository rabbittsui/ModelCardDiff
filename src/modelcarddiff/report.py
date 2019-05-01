"""Line-oriented rendering of gate, diff, and claims output.

Every renderer returns a list of strings, one per output line, so the CLI can
print them and the tests can assert on them without worrying about trailing
newlines. Output is deterministic: the same card and schema always produce the
same lines in the same order.
"""

from __future__ import annotations

from .card import Card
from .claims import Citation, resolve_citations
from .diff import (
    ADDED_CLAIM,
    EDITORIAL,
    METRIC_REGRESSION,
    REMOVED_LIMITATION,
    Change,
)
from .gate import GateResult

_CHANGE_LABELS = {
    ADDED_CLAIM: "added claim",
    REMOVED_LIMITATION: "removed limitation",
    METRIC_REGRESSION: "metric regression",
    EDITORIAL: "editorial",
}


def render_gate(result: GateResult, card_name: str) -> list[str]:
    """Render a gate result.

    On pass, a single PASS line. On refuse, a REFUSE line with the count
    followed by one indented line per finding, each prefixed by its code.
    """
    if result.passed:
        return [f"PASS {card_name}: all checks satisfied"]
    lines = [f"REFUSE {card_name}: {len(result.findings)} finding(s)"]
    for finding in result.findings:
        location = f" (line {finding.line})" if finding.line else ""
        lines.append(f"  [{finding.code}]{location} {finding.message}")
    return lines


def render_claims(card: Card, card_name: str) -> list[str]:
    """Render the claim to citation table for a card.

    One line per claim showing whether it is cited, dangling, or resolved, and
    the evaluation it points at. A trailing summary counts each kind.
    """
    citations = resolve_citations(card)
    lines = [f"claims for {card_name}: {len(citations)}"]
    resolved = 0
    uncited = 0
    dangling = 0
    for citation in citations:
        lines.append(_claim_line(citation))
        if citation.uncited:
            uncited += 1
        elif citation.dangling:
            dangling += 1
        else:
            resolved += 1
    lines.append(
        f"summary: {resolved} resolved, {uncited} uncited, {dangling} dangling"
    )
    return lines
