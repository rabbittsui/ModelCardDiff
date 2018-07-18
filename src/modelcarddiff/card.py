"""Parse the model card format into sections, claims, and results.

Card format
-----------

A card is Markdown with a small set of conventions:

- ``## Section Name`` starts a section. Everything until the next ``##`` heading
  is the body of that section. A leading ``# Title`` line is treated as the card
  title, not a section.
- A capability claim is a bullet in the Capabilities section written as::

      - claim: <text> (cites: <eval-id>)

  The ``(cites: <eval-id>)`` suffix is optional. A claim without it is an
  uncited claim, recorded with ``cites`` set to ``None``.
- A limitation is any bullet in the Limitations section.
- A result is a line in the Results section written as::

      <eval-id> = <metric-name> <value>

  The value is parsed as a float when possible, otherwise kept as text.

The parser is deliberately forgiving about surrounding whitespace and blank
lines, and strict about the shape of claim and result lines so that malformed
input is visible rather than silently dropped.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CLAIM_PREFIX = "claim:"
_CITES_RE = re.compile(r"\(cites:\s*([^)]+?)\s*\)\s*$")
_RESULT_RE = re.compile(r"^(?P<eval>[^=]+?)\s*=\s*(?P<metric>\S+)\s+(?P<value>.+?)\s*$")


@dataclass(frozen=True)
class Claim:
    """A single capability claim.

    text is the claim sentence with the ``(cites: ...)`` suffix removed.
    cites is the referenced evaluation id, or None when the claim cites nothing.
    line is the 1 based line number in the source card.
    """

    text: str
    cites: str | None
    line: int


@dataclass(frozen=True)
class Result:
    """A single evaluation result.

    eval_id is the identifier a claim may cite.
    metric is the metric name, for example ``accuracy``.
    value_text is the raw value token as written.
    value is the float parse of value_text, or None when it is not numeric.
    line is the 1 based line number in the source card.
    """

    eval_id: str
    metric: str
    value_text: str
    value: float | None
    line: int


@dataclass
class Section:
    """A card section: a heading and its non-empty body lines."""

    name: str
    body_lines: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """True when the section has no non-blank body line."""
        return all(not line.strip() for line in self.body_lines)

    def text(self) -> str:
        """Return the body joined and stripped, for display and hashing."""
        return "\n".join(self.body_lines).strip()


@dataclass
class Card:
    """A parsed model card."""

    title: str
    sections: list[Section]
    claims: list[Claim]
    limitations: list[str]
    results: list[Result]

    def section(self, name: str) -> Section | None:
        """Return the section matched case insensitively by name, or None."""
        target = name.strip().lower()
        for sec in self.sections:
            if sec.name.strip().lower() == target:
                return sec
        return None

    def result_ids(self) -> set[str]:
        """Return the set of evaluation ids present in Results."""
        return {r.eval_id for r in self.results}

    def result_by_id(self, eval_id: str) -> Result | None:
        """Return the result with the given id, or None."""
        for r in self.results:
            if r.eval_id == eval_id:
