import argparse
import sys
from typing import Any

from slopcheck import render
from slopcheck.scorer import analyze


def main() -> None:
    """
    CLI entry point for slopcheck.
    
    Parses command-line arguments, reads input from a file or stdin, calls the
    analyzer, and delegates rendering to the print_report/print_json helpers.
    
    Exit codes:
        - 0 if risk_band is not "high"
        - 1 if risk_band is "high" (usable as CI gate)
        - 2 on file-not-found or read errors
    """
    parser = argparse.ArgumentParser(
        description="slopcheck: A command-line tool to analyze text for AI-writing signatures."
    )
    parser.add_argument(
        "file",
        help="The path to the text file to analyze. Use '-' to read from standard input."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the analysis results as machine-readable JSON to stdout."
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Include detailed matched phrase spans with their context and line numbers."
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in the terminal report (ideal for CI/non-tty outputs)."
    )

    args = parser.parse_args()

    # Read from file or standard input
    try:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found: {args.file}\n")
        sys.exit(2)
    except Exception as e:
        sys.stderr.write(f"Error reading file: {e}\n")
        sys.exit(2)

    # Perform composite analysis
    try:
        result = analyze(text)
    except Exception as e:
        sys.stderr.write(f"Error during analysis: {e}\n")
        sys.exit(2)

    # Respect --no-color flag and redirect targets (non-tty environments)
    color = not args.no_color
    if not sys.stdout.isatty():
        color = False

    # Render outputs
    if args.json:
        render.print_json(result)
    else:
        render.print_report(result, text=text, explain=args.explain, color=color)

    # Determine exit code based on the risk band
    if result.get("risk_band") == "high":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
