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
