"""The requirements schema and required section resolution.

Schema format
-------------

One directive per line. Blank lines and lines beginning with ``#`` are ignored::

    require <Section Name>

Each ``require`` names a section that must exist in the card and must be
