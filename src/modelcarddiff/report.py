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


def _claim_line(citation: Citation) -> str:
    """Render one claim citation line."""
    if citation.uncited:
        status = "UNCITED"
        target = "-"
    elif citation.dangling:
        status = "DANGLING"
        target = citation.cited_id or "-"
    else:
        status = "CITES"
        target = citation.cited_id or "-"
    return f"  {status:<8} {target:<28} {citation.claim.text}"


def render_diff(changes: list[Change], old_name: str, new_name: str) -> list[str]:
    """Render the classified changes between two versions.

    A header names the two versions. Each change is one line prefixed by its
    kind label. A trailing summary counts each kind so a reader sees at a glance
    whether a limitation was dropped or a metric regressed.
    """
    lines = [f"diff {old_name} -> {new_name}: {len(changes)} change(s)"]
    for change in changes:
        label = _CHANGE_LABELS.get(change.kind, change.kind)
        lines.append(f"  [{label}] {change.detail}")
    counts = _count_kinds(changes)
    lines.append(
        "summary: "
        + ", ".join(
            f"{counts[kind]} {_CHANGE_LABELS[kind]}"
            for kind in (ADDED_CLAIM, REMOVED_LIMITATION, METRIC_REGRESSION, EDITORIAL)
        )
    )
    return lines


def _count_kinds(changes: list[Change]) -> dict[str, int]:
    """Count changes by kind, with every known kind present."""
    counts = {
        ADDED_CLAIM: 0,
        REMOVED_LIMITATION: 0,
        METRIC_REGRESSION: 0,
        EDITORIAL: 0,
    }
    for change in changes:
        counts[change.kind] = counts.get(change.kind, 0) + 1
    return counts
