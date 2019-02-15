"""Command line interface for modelcarddiff.

Subcommands:

    gate     check a card against a schema and pass or refuse
    diff     compare two card versions and classify each change
    claims   show which evaluation each capability claim cites
    version  print the package version

Exit codes: 0 clean, 1 findings present (gate refused or a regression found),
2 usage error. argparse itself exits with 2 on argument errors, which matches
the standard.
"""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__, diff as diff_mod, report
from .card import parse_file as parse_card_file
from .gate import gate
from .schema import SchemaError, parse_file as parse_schema_file


def _display_name(path: str) -> str:
    """Return a stable base name for a path, for use in output lines."""
    return os.path.basename(path.replace("\\", "/"))


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        print(line)


def _cmd_gate(args: argparse.Namespace) -> int:
    try:
        schema = parse_schema_file(args.schema)
    except SchemaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    card = parse_card_file(args.card)
