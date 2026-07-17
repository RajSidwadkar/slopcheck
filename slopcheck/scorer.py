import os
from importlib import resources
from typing import Any

from slopcheck.signals.phrases import load_phrase_bank, score_phrases
from slopcheck.signals.rhythm import score_rhythm
from slopcheck.signals.punctuation import score_punctuation
from slopcheck.signals.structure import score_structure
from slopcheck.signals.lexical import score_lexical

# Resolve the default phrase bank path relative to the package using importlib.resources
try:
    pkg_path = resources.files("slopcheck")
    DEFAULT_PHRASE_BANK_PATH = str(pkg_path.parent / "data" / "phrase_bank.json")
except Exception:
    # Fallback to file system path resolution relative to scorer.py location
    DEFAULT_PHRASE_BANK_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "phrase_bank.json",
    )


def analyze(text: str, phrase_bank: dict[str, int] | None = None) -> dict[str, Any]:
    """
    Analyze the input text across all 5 writing signals and return a composite risk report.
    
    The composite score is the sum of:
        - phrases (0-40)
        - rhythm (0-20)
        - punctuation (0-15)
        - structure (0-15)
        - lexical (0-10)
        
    Total score ranges from 0 to 100.
    
    Args:
        text: The input text to analyze.
        phrase_bank: An optional dictionary mapping phrases to weights. If None,
                     the default phrase bank is loaded from data/phrase_bank.json.
                     
    Returns:
        A dictionary containing:
            - "total_score": The sum of all 5 sub-scores (0-100).
            - "risk_band": The risk classification ("low" <35, "medium" 35-69, "high" >=70).
            - "signals": A dictionary mapping each signal name to its score and detail.
    """
    if phrase_bank is None:
        phrase_bank = load_phrase_bank(DEFAULT_PHRASE_BANK_PATH)

    # Call each of the 5 scoring signals
    phrase_score, phrase_matches = score_phrases(text, phrase_bank)
    rhythm_score, rhythm_detail = score_rhythm(text)
    punctuation_score, punctuation_detail = score_punctuation(text)
    structure_score, structure_detail = score_structure(text)
    lexical_score, lexical_detail = score_lexical(text)

    # Compute composite score
    total_score = (
        phrase_score
        + rhythm_score
        + punctuation_score
        + structure_score
        + lexical_score
    )

    # Classify the risk band
    if total_score < 35.0:
        risk_band = "low"
    elif total_score >= 70.0:
        risk_band = "high"
    else:
        risk_band = "medium"

    return {
        "total_score": total_score,
        "risk_band": risk_band,
        "signals": {
            "phrases": {
                "score": phrase_score,
                "matches": phrase_matches,
            },
            "rhythm": {
                "score": rhythm_score,
                "detail": rhythm_detail,
            },
            "punctuation": {
                "score": punctuation_score,
                "detail": punctuation_detail,
            },
            "structure": {
                "score": structure_score,
                "detail": structure_detail,
            },
            "lexical": {
                "score": lexical_score,
                "detail": lexical_detail,
            },
        },
    }
