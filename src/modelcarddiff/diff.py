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
