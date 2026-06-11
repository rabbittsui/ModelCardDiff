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
    """The outcome of gating one card."""

    findings: list[Finding] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True when there are no findings."""
        return not self.findings

    @property
    def refused(self) -> bool:
        """True when at least one finding was recorded."""
        return bool(self.findings)


def gate(card: Card, schema: Schema) -> GateResult:
    """Run every check and return the ordered findings."""
    findings: list[Finding] = []

    # 1. Required sections.
    for status in resolve_sections(schema, card):
        if not status.present:
            findings.append(
                Finding(
                    code=MISSING_SECTION,
                    message=f"required section {status.name!r} is missing",
                )
            )
        elif not status.non_empty:
            findings.append(
                Finding(
                    code=EMPTY_SECTION,
                    message=f"required section {status.name!r} is present but empty",
                )
            )

    # 2. Citations: uncited then dangling, each in card order.
    for claim in claims_mod.uncited_claims(card):
        findings.append(
            Finding(
                code=UNCITED_CLAIM,
                message=f"claim cites no evaluation: {claim.text}",
                line=claim.line,
            )
        )
    for citation in claims_mod.dangling_claims(card):
        findings.append(
            Finding(
                code=DANGLING_CITATION,
                message=(
                    f"claim cites {citation.cited_id!r} which is not in results: "
                    f"{citation.claim.text}"
                ),
                line=citation.claim.line,
            )
        )

    # 3. Metric quotes.
    for quote in claims_mod.unmatched_metric_quotes(card):
        findings.append(
            Finding(
                code=UNMATCHED_METRIC,
                message=(
                    f"claim quotes {quote.quoted} which no result value matches: "
                    f"{quote.claim.text}"
                ),
                line=quote.claim.line,
            )
        )

    # 4. Distinct limitations.
    for dup in claims_mod.duplicate_limitations(card):
        findings.append(
            Finding(
                code=DUPLICATE_LIMITATION,
                message=(
                    f"limitation {dup.second_index + 1} repeats limitation "
                    f"{dup.first_index + 1}: {dup.text}"
                ),
            )
        )

    return GateResult(findings=findings)
