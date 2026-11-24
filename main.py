#!/usr/bin/env python3
"""Last Text at One Percent — write the phone's final text to entry.txt.

The entry is one line, exactly 145 characters, written with no trailing
newline so the file is byte-identical to the line itself.

Usage:
    python3 main.py              write entry.txt into $MAKEFUN_OUTPUT_DIR
    python3 main.py --check      validate the line only, write nothing
    python3 main.py --self-test  validate, then prove a byte-identical
                                 write/read round-trip in a temp dir
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

# The phone's last text, in its own voice. 145 characters, inside the
# competition's 1-200 character gate. The em-dash is a single character.
LINE = (
    "1% left. Tell the charger I loved it. "
    "Tell the group chat I read everything and replied to nothing. "
    "Goodbye, human \u2014 it was fun being your brain."
)


def validate(line: str) -> None:
    """Refuse anything that would fail the sealed gate."""
    if not line:
        raise ValueError("entry is empty")
    if len(line) > 200:
        raise ValueError(f"entry is {len(line)} characters, over the 200 limit")
    if not line.strip():
        raise ValueError("entry is only whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("entry must be a single line")


def write_entry(directory: str | os.PathLike) -> Path:
    """Write the line to entry.txt in directory, no trailing newline."""
    target = Path(directory) / "entry.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(LINE.encode("utf-8"))
    return target


def check_round_trip(directory: str | os.PathLike) -> Path:
    """Write entry.txt, read it back, and demand byte-identical content."""
    target = write_entry(directory)
    back = target.read_bytes()
    if back != LINE.encode("utf-8"):
        raise ValueError(
            f"round-trip mismatch: wrote {len(LINE.encode('utf-8'))} bytes, "
            f"read back {len(back)} bytes"
        )
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the entry line only; write nothing",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="validate, then verify a byte-identical write/read round-trip "
        "in a temporary directory",
    )
    args = parser.parse_args(argv)

    try:
        validate(LINE)
    except ValueError as exc:
        print(f"invalid entry: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(f"entry valid: {len(LINE)} characters, {len(LINE.encode('utf-8'))} bytes")
        return 0

    if args.self_test:
        with tempfile.TemporaryDirectory(prefix="last-text-self-test-") as tmp:
            target = check_round_trip(tmp)
        print(f"self-test ok: {target.name} round-trips byte-identical "
              f"({len(LINE)} characters)")
        return 0

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = check_round_trip(out_dir)
    print(f"wrote {target} ({len(LINE)} characters, no trailing newline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
