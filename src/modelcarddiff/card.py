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
                return r
        return None


def _strip_bullet(line: str) -> str | None:
    """Return the bullet text if line is a ``-`` or ``*`` bullet, else None."""
    stripped = line.strip()
    if stripped.startswith("- "):
        return stripped[2:].strip()
    if stripped.startswith("* "):
        return stripped[2:].strip()
    return None


def _parse_claim(bullet_text: str, line_no: int) -> Claim | None:
    """Parse a bullet into a Claim, or None when it is not a claim bullet."""
    if not bullet_text.lower().startswith(CLAIM_PREFIX):
        return None
    body = bullet_text[len(CLAIM_PREFIX):].strip()
    cites: str | None = None
    match = _CITES_RE.search(body)
    if match is not None:
        cites = match.group(1).strip()
        body = body[: match.start()].strip()
    return Claim(text=body, cites=cites, line=line_no)


def _parse_result(line: str, line_no: int) -> Result | None:
    """Parse a Results line into a Result, or None when it does not match."""
    match = _RESULT_RE.match(line)
    if match is None:
        return None
    value_text = match.group("value").strip()
    try:
        value: float | None = float(value_text)
    except ValueError:
        value = None
    return Result(
        eval_id=match.group("eval").strip(),
        metric=match.group("metric").strip(),
        value_text=value_text,
        value=value,
        line=line_no,
    )


def parse(text: str) -> Card:
    """Parse card text into a Card.

    The parser is single pass. It tracks the current section and, when inside
    the Capabilities, Limitations, or Results sections, interprets the lines
    with the section specific rules.
    """
    title = ""
    sections: list[Section] = []
    current: Section | None = None
    claims: list[Claim] = []
    limitations: list[str] = []
    results: list[Result] = []

    lines = text.splitlines()
    for index, raw in enumerate(lines):
        line_no = index + 1
        stripped = raw.strip()

        if stripped.startswith("## "):
            current = Section(name=stripped[3:].strip())
            sections.append(current)
            continue
        if stripped.startswith("# "):
            # Card title. Only the first title line is recorded.
            if not title:
                title = stripped[2:].strip()
            continue

        if current is not None:
            current.body_lines.append(raw)

        section_name = current.name.lower() if current is not None else ""

        if section_name == "capabilities":
            bullet = _strip_bullet(raw)
            if bullet is not None:
                claim = _parse_claim(bullet, line_no)
                if claim is not None:
                    claims.append(claim)
        elif section_name == "limitations":
            bullet = _strip_bullet(raw)
            if bullet is not None:
                limitations.append(bullet)
        elif section_name == "results":
            if stripped and not stripped.startswith("#"):
                result = _parse_result(stripped, line_no)
                if result is not None:
                    results.append(result)

    return Card(
        title=title,
        sections=sections,
        claims=claims,
        limitations=limitations,
        results=results,
    )


def parse_file(path: str) -> Card:
    """Read and parse a card file using UTF-8."""
    with open(path, "r", encoding="utf-8") as handle:
        return parse(handle.read())

# draft note 937
