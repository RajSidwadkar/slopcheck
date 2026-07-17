import json
from typing import Any


def print_json(result: dict[str, Any]) -> None:
    """
    Print the analysis result dictionary as formatted JSON to stdout.
    
    Args:
        result: The analysis result dictionary from scorer.analyze().
    """
    # Create a copy without the internal metadata keys
    clean_result = {k: v for k, v in result.items() if not k.startswith("_")}
    print(json.dumps(clean_result, indent=2))


def print_report(result: dict[str, Any], explain: bool = False, color: bool = True) -> None:
    """
    Print a user-friendly report of the analysis results to stdout.
    
    Args:
        result: The analysis result dictionary from scorer.analyze().
        explain: If True, include details of each matched phrase with line numbers.
        color: If True, utilize ANSI escape codes to colorize output.
    """
    # ANSI color codes
    GREEN = "\033[32m" if color else ""
    YELLOW = "\033[33m" if color else ""
    RED = "\033[31m" if color else ""
    RESET = "\033[0m" if color else ""
    BOLD = "\033[1m" if color else ""

    # Extract metadata added by cli.py
    filename = result.get("_filename", "<unknown>")
    text = result.get("_text", "")

    total_score = result["total_score"]
    risk_band = result["risk_band"]

    # Select color coding based on the risk band
    if risk_band == "low":
        band_color = GREEN
    elif risk_band == "medium":
        band_color = YELLOW
    else:
        band_color = RED

    rounded_score = int(round(total_score))

    # Print Header and Score
    print(f"slopcheck: {filename}")
    print(f"Score: {band_color}{rounded_score}/100{RESET}  ({band_color}{risk_band} AI-signal density{RESET})")
    print()

    # Print Signals breakdown (aligned perfectly)
    signals = result["signals"]
    phrase_score = signals["phrases"]["score"]
    rhythm_score = signals["rhythm"]["score"]
    punctuation_score = signals["punctuation"]["score"]
    structure_score = signals["structure"]["score"]
    lexical_score = signals["lexical"]["score"]

    print(f"  Phrase matches        {int(round(phrase_score)):>2}/40")
    print(f"  Sentence rhythm       {int(round(rhythm_score)):>2}/20")
    print(f"  Punctuation           {int(round(punctuation_score)):>2}/15")
    print(f"  Paragraph uniformity  {int(round(structure_score)):>2}/15")
    print(f"  Lexical diversity     {int(round(lexical_score)):>2}/10")

    # Print explanation if requested
    if explain and "phrases" in signals:
        matches = signals["phrases"]["matches"]
        if matches:
            print()
            print("Flagged spans:")
            for m in matches:
                pos = m["position"]
                snippet = m["context_snippet"].replace("\n", " ")
                
                # Compute line number from char position
                line_no = 1
                if text:
                    line_no = text[:pos].count("\n") + 1
                    
                print(f"    L{line_no}: \"...{snippet}...\"")

    # Print Warning/Disclaimer
    print()
    print("  ⚠ Heuristic estimate, not proof. False positives common in formal/corporate writing")
    print("    and non-native English styles.")
