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
