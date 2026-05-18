"""
Command-line interface for the state_surfaces package.

This module intentionally stays thin: it parses CLI arguments, delegates
computation to `pipeline.run_pipeline`, and prints the result.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Optional

from .pipeline import run_pipeline


def _read_text(path: str) -> str:
    """Read a text file, or read from stdin if path is '-'."""
    if path == "-":
        return sys.stdin.read()

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_input_value(raw: str) -> Any:
    """
    Parse user input as JSON when possible.

    If JSON parsing fails, return the stripped string unchanged. This allows
    users to pass JSON-style Gauss or DT codes directly on the command line.
    """
    raw = raw.strip()
    if not raw:
        return raw

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _format_output(result: dict[str, Any], pretty: bool = False) -> str:
    """
    Format command-line output.

    In compact mode, return machine-readable JSON. In pretty mode, display
    fields in a stable order while keeping Gauss codes and state codes on one
    line. State circles are displayed using tuple notation.
    """
    if not pretty:
        return json.dumps(result, sort_keys=True)

    ordered_keys = [
        "gauss_code",
        "state_code",
        "unoriented_genus",
        "crosscap",
        "simple",
        "two_sided",
    ]

    items = [(key, result[key]) for key in ordered_keys if key in result]
    lines = ["{"]

    for idx, (key, value) in enumerate(items):
        comma = "," if idx < len(items) - 1 else ""

        if key == "state_code":
            circles = ", ".join(str(tuple(circle)) for circle in value)
            value_str = f"[{circles}]"
        elif key == "gauss_code":
            value_str = json.dumps(value)
        else:
            value_str = json.dumps(value)

        lines.append(f'  "{key}": {value_str}{comma}')

    lines.append("}")
    return "\n".join(lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="state_surfaces",
        description="Compute state codes and invariants from Gauss or DT codes.",
    )

    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--gauss",
        type=str,
        help="Gauss code input as a string or JSON-style list.",
    )
    src.add_argument(
        "--dt",
        type=str,
        help="DT code input as a string or JSON-style list.",
    )
    src.add_argument(
        "--file",
        type=str,
        help="Read input from a file, or use '-' for stdin. Requires --as.",
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
        help="Pretty-print output.",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Run the command-line interface."""
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

    sys.stdout.write(_format_output(result, pretty=args.pretty))
    sys.stdout.write("\n")

    return 0


__all__ = ["main"]
