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

# Comparison words that turn a following number into a bound rather than an
# exact quote of a measured value. A claim of "accuracy above 0.90" states a
# threshold the model clears, not that the measured accuracy equals 0.90, so it
# is checked only for the metric it cites, not for an exact value match. A claim
# of "accuracy of 0.99" quotes an exact value and must match a result.
_BOUND_WORDS = frozenset(
    {
        "above",
        "below",
        "under",
        "over",
        "least",
        "most",
        "than",
        "up",
        "within",
        "exceeds",
        "exceed",
        "beyond",
        "near",
        "around",
        "about",
        "approximately",
    }
)

# Words that carry no information on their own. Two limitations that reduce to
# the same set of remaining words after removing these are treated as the same
# statement.
_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "is",
        "are",
        "it",
        "its",
        "so",
        "that",
        "this",
        "with",
        "for",
        "not",
        "than",
        "do",
        "does",
        "only",
        "more",
        "other",
        "they",
        "because",
    }
)


@dataclass(frozen=True)
class Citation:
    """Resolution of a single claim's citation.

    cited_id is the evaluation id the claim references, or None when uncited.
    resolved is True when cited_id names a result present in the card.
    """

    claim: Claim
    cited_id: str | None
    resolved: bool

    @property
    def uncited(self) -> bool:
        """True when the claim cites nothing."""
        return self.cited_id is None

    @property
    def dangling(self) -> bool:
        """True when the claim cites an id that no result provides."""
        return self.cited_id is not None and not self.resolved


@dataclass(frozen=True)
class MetricQuote:
    """A number quoted in a claim and whether a result carries that value.

    quoted is the numeric token as written in the claim.
    matched is True when some result value equals the quoted number.
    """

    claim: Claim
    quoted: str
    matched: bool


@dataclass(frozen=True)
class DuplicateLimitation:
    """Two limitations that reduce to the same content words."""

    first_index: int
    second_index: int
    text: str


def resolve_citations(card: Card) -> list[Citation]:
    """Resolve every capability claim against the results.

    A claim that cites an id present in the results resolves. A claim that cites
    an id no result provides is dangling. A claim that cites nothing is uncited.
    """
    ids = card.result_ids()
    citations: list[Citation] = []
    for claim in card.claims:
        if claim.cites is None:
            citations.append(Citation(claim=claim, cited_id=None, resolved=False))
        else:
            citations.append(
                Citation(
                    claim=claim,
                    cited_id=claim.cites,
                    resolved=claim.cites in ids,
                )
            )
    return citations


def uncited_claims(card: Card) -> list[Claim]:
    """Return the claims that cite nothing, in card order."""
    return [c.claim for c in resolve_citations(card) if c.uncited]


def dangling_claims(card: Card) -> list[Citation]:
    """Return citations that reference an id absent from the results."""
    return [c for c in resolve_citations(card) if c.dangling]


def _result_value_strings(card: Card) -> set[str]:
    """Return every result value as a normalized numeric string.

    A value like 0.90 and 0.9 should compare equal, so numeric values are
    normalized through float and back. Non-numeric values are kept verbatim.
    """
    values: set[str] = set()
    for result in card.results:
        if result.value is not None:
            values.add(_normalize_number(result.value))
        else:
            values.add(result.value_text)
    return values


def _normalize_number(value: float) -> str:
    """Return a canonical string for a float so 0.90 and 0.9 match."""
    if value == int(value):
        return str(int(value))
    return repr(value)


def metric_quotes(card: Card) -> list[MetricQuote]:
    """Find exact metric values quoted in claims and whether a result has each.

    Only claims that cite a resolvable result are checked, because a quoted
    value is meant to come from the cited evaluation. A number introduced by a
    comparison word (above, under, at least, and the like) is a bound, not an
    exact value, so it is not checked for a value match. A number stated
    directly, as in "accuracy of 0.99", is an exact quote: if no result carries
    it, the claim quotes a metric value absent from the results.
    """
    ids = card.result_ids()
    quotes: list[MetricQuote] = []
    for claim in card.claims:
        if claim.cites is None or claim.cites not in ids:
