"""
cli.py

Command-line interface for the state_surfaces package.

This module intentionally stays thin: it parses CLI args, delegates computation
to `pipeline.run_pipeline`, and prints results in a machine-friendly format.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from .pipeline import run_pipeline


def _read_text(path: str) -> str:
    """Read a text file (or stdin if path == '-')."""
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_input_value(raw: str) -> Any:
    """
    Try to parse user input as JSON first; if that fails, return as a string.

    This lets users pass:
      --gauss "[[1,2,3,1],[2,3,4,4]]"
      --dt "[[4,6,8]]"
    or other JSON-like structures without special casing.
    """
    raw = raw.strip()
    if not raw:
        return raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="state_surfaces",
        description="Compute state codes and invariants from Gauss or DT codes.",
    )

    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--gauss",
        type=str,
        help="Gauss code input (string notation or JSON).",
    )
    src.add_argument(
        "--dt",
        type=str,
        help="DT code input (string or JSON).",
    )
    src.add_argument(
        "--file",
        type=str,
        help="Read input from a file (use '-' for stdin). Requires --as.",
    )

    parser.add_argument(
        "--as",
        dest="assume",
        choices=("gauss", "dt"),
        default=None,
        help="When using --file, specify whether the file contains a Gauss code or DT code.",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    gauss_code = None
    dt_code = None

    if args.gauss is not None:
        gauss_code = _parse_input_value(args.gauss)

    elif args.dt is not None:
        dt_code = _parse_input_value(args.dt)

    else:
        if args.assume is None:
            parser.error("--file requires --as {gauss,dt}.")
        text = _read_text(args.file)
        if args.assume == "gauss":
            gauss_code = _parse_input_value(text)
        else:
            dt_code = _parse_input_value(text)

    result = run_pipeline(gauss_code=gauss_code, dt_code=dt_code)

    indent = 2 if args.pretty else None
    sys.stdout.write(json.dumps(result, indent=indent, sort_keys=True))
    sys.stdout.write("\n")
    return 0


__all__ = ["main"]
