import json
from typing import Any


def print_json(result: dict[str, Any]) -> None:
    """
    Print the analysis result dictionary as formatted JSON to stdout.
    
    Args:
        result: The analysis result dictionary from scorer.analyze().
    """
    print(json.dumps(result, indent=2))


def print_report(
    result: dict[str, Any],
    text: str = "",
    explain: bool = False,
    color: bool = True,
) -> None:
    """
    Print a user-friendly colored report of the analysis results to stdout.
    
    Args:
        result: The analysis result dictionary from scorer.analyze().
        text: The original text analyzed, used to calculate match line numbers.
        explain: If True, include details of each matched phrase with line numbers.
        color: If True, utilize ANSI escape codes to colorize output.
    """
    # ANSI color and styling escape codes
    GREEN = "\033[92m" if color else ""
    YELLOW = "\033[93m" if color else ""
    RED = "\033[91m" if color else ""
    RESET = "\033[0m" if color else ""
    BOLD = "\033[1m" if color else ""
    CYAN = "\033[96m" if color else ""

    total_score = result["total_score"]
    risk_band = result["risk_band"]

    # Select color coding based on the risk band
    if risk_band == "low":
        band_color = GREEN
    elif risk_band == "medium":
        band_color = YELLOW
    else:
        band_color = RED

    print(f"{BOLD}Slopcheck Analysis Report{RESET}")
    print("=========================")
    print(f"Total Score: {band_color}{total_score:.1f}/100{RESET} ({band_color}{risk_band.upper()} RISK{RESET})")
    print()
    print(f"{BOLD}Signals Summary:{RESET}")
    
    signals = result["signals"]
    for name, data in signals.items():
        score = data["score"]
        
        # Look up correct maximum scale for each signal type
        max_score = 0
        if name == "phrases":
            max_score = 40
        elif name == "rhythm":
            max_score = 20
        elif name in ("punctuation", "structure"):
            max_score = 15
        elif name == "lexical":
            max_score = 10
            
        print(f"  - {name.capitalize():<12}: {score:>5.1f} / {max_score}")

    if explain and "phrases" in signals:
        matches = signals["phrases"]["matches"]
        if matches:
            print()
            print(f"{BOLD}Matched AI-Writing Phrases:{RESET}")
            print("---------------------------")
            
            for m in matches:
                pos = m["position"]
                phrase = m["phrase"]
                weight = m["weight"]
                snippet = m["context_snippet"].replace("\n", " ")
                
                # Compute line number from char position
                line_no = 1
                if text:
                    line_no = text[:pos].count("\n") + 1
                    
                print(f"  Line {line_no:<4} | Phrase: {RED}{phrase:<25}{RESET} (Weight: {weight})")
                print(f"            Context: \"...{CYAN}{snippet}{RESET}...\"")
        else:
            print()
            print("No matching AI-writing phrases detected.")
