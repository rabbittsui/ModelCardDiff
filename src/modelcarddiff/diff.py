"""Version comparison and change classification.

Given two parsed cards, an old and a new version, this module classifies every
change into one of four kinds:

- ``added-claim``       a capability claim present in new but not old.
- ``removed-limitation`` a limitation present in old but not new. This is the
  change most worth catching, because a quietly dropped limitation weakens the
  honest description of the model without touching a metric.
- ``metric-regression`` a result value that moved in the worse direction. The
  direction that counts as worse depends on the metric: for a rate whose name
  contains ``confusion``, ``error``, ``loss``, or ``latency`` a rise is a
  regression, and for everything else a fall is a regression.
- ``editorial``         any other textual change: a reworded claim or
  limitation, a section body edit, or an added or removed result that is not a
  regression.

The classification is deterministic and order stable. Metric regressions are
reported before removed limitations only in code order; the report groups them
by kind for reading.
"""

from __future__ import annotations

from dataclasses import dataclass

from .card import Card, Result

ADDED_CLAIM = "added-claim"
REMOVED_LIMITATION = "removed-limitation"
METRIC_REGRESSION = "metric-regression"
EDITORIAL = "editorial"

# Metric name fragments where a higher value is worse. For every other metric a
# lower value is treated as the regression.
_HIGHER_IS_WORSE = ("confusion", "error", "loss", "latency", "regression")


@dataclass(frozen=True)
class Change:
    """One classified change between two card versions.

    kind is one of the four change codes above.
    detail is a human readable description of the change.
    """

    kind: str
    detail: str


def _metric_higher_is_worse(metric: str, eval_id: str) -> bool:
    """Return True when a rise in this metric is a regression."""
    haystack = f"{eval_id} {metric}".lower()
    return any(fragment in haystack for fragment in _HIGHER_IS_WORSE)


def _classify_metric(old: Result, new: Result) -> Change | None:
    """Classify a metric change, returning a regression Change or None.

    A non-numeric change, or a numeric change in the improving direction, is not
    a regression and is reported as editorial by the caller when the text
    differs.
    """
    if old.value is None or new.value is None:
        return None
    if new.value == old.value:
        return None
    higher_is_worse = _metric_higher_is_worse(new.metric, new.eval_id)
    worse = new.value > old.value if higher_is_worse else new.value < old.value
    if not worse:
        return None
    direction = "rose" if new.value > old.value else "fell"
    return Change(
        kind=METRIC_REGRESSION,
        detail=(
            f"{new.eval_id} {new.metric} {direction} from {old.value_text} "
            f"to {new.value_text}"
        ),
    )


def diff(old: Card, new: Card) -> list[Change]:
    """Compare two cards and return the classified changes in a stable order.

    The order is: added claims, removed limitations, metric regressions, then
    editorial changes. Within each kind the order follows the source cards.
    """
    added: list[Change] = []
    removed: list[Change] = []
    regressions: list[Change] = []
    editorial: list[Change] = []

    old_claims = {c.text for c in old.claims}
    new_claims = {c.text for c in new.claims}

    for claim in new.claims:
        if claim.text not in old_claims:
            added.append(Change(kind=ADDED_CLAIM, detail=claim.text))
    for claim in old.claims:
        if claim.text not in new_claims:
            editorial.append(
                Change(kind=EDITORIAL, detail=f"claim removed: {claim.text}")
            )

    old_lims = list(old.limitations)
    new_lims_set = set(new.limitations)
    for limitation in old_lims:
        if limitation not in new_lims_set:
            removed.append(Change(kind=REMOVED_LIMITATION, detail=limitation))
