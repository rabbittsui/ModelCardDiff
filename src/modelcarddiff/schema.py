"""The requirements schema and required section resolution.

Schema format
-------------

One directive per line. Blank lines and lines beginning with ``#`` are ignored::

    require <Section Name>

Each ``require`` names a section that must exist in the card and must be
non-empty. Section names are matched case insensitively.

The schema is intentionally small. It answers one question: which sections must
a conforming card contain. The gate combines that answer with the claim and
metric checks in :mod:`modelcarddiff.gate`.
"""

from __future__ import annotations

from dataclasses import dataclass

from .card import Card

REQUIRE_DIRECTIVE = "require"


@dataclass(frozen=True)
class Schema:
    """A requirements schema: an ordered list of required section names."""

    required_sections: tuple[str, ...]


class SchemaError(ValueError):
    """Raised when a schema line cannot be understood."""


def parse(text: str) -> Schema:
    """Parse schema text into a Schema.

    Duplicate ``require`` directives are collapsed while preserving first-seen
    order, so a schema that lists a section twice does not report it twice.
    """
    required: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(text.splitlines()):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        directive = parts[0].lower()
        if directive != REQUIRE_DIRECTIVE:
            raise SchemaError(
                f"line {index + 1}: unknown directive {parts[0]!r}, "
                f"expected {REQUIRE_DIRECTIVE!r}"
            )
        if len(parts) < 2 or not parts[1].strip():
            raise SchemaError(f"line {index + 1}: require needs a section name")
        name = parts[1].strip()
        key = name.lower()
        if key not in seen:
            seen.add(key)
            required.append(name)
    return Schema(required_sections=tuple(required))


def parse_file(path: str) -> Schema:
    """Read and parse a schema file using UTF-8."""
    with open(path, "r", encoding="utf-8") as handle:
        return parse(handle.read())


@dataclass(frozen=True)
class SectionStatus:
    """Resolution of one required section against a card.

    present is True when the card has a section with the required name.
    non_empty is True when that section has a non-blank body.
    """

    name: str
