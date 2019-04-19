"""Line-oriented rendering of gate, diff, and claims output.

Every renderer returns a list of strings, one per output line, so the CLI can
print them and the tests can assert on them without worrying about trailing
newlines. Output is deterministic: the same card and schema always produce the
same lines in the same order.
"""

from __future__ import annotations

from .card import Card
