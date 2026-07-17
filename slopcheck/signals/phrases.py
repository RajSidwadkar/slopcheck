import json
import re
from typing import Any, NamedTuple


class MatchInfo(NamedTuple):
    """Internal helper to store match information for overlap resolution."""
    start: int
    end: int
    phrase: str
    weight: int
    matched_text: str


def _compile_pattern(phrase: str) -> re.Pattern[str]:
    """
    Compile a phrase or construction into a case-insensitive regular expression pattern.
    
    If the phrase contains regex metacharacters, it is compiled as-is.
    Otherwise, it is compiled with word boundaries at the start and end
    where appropriate (i.e. if the first/last characters are alphanumeric).
    """
    if any(c in phrase for c in "*[(|\\"):
        return re.compile(phrase, re.IGNORECASE)
    
    start_boundary = r"\b" if phrase and (phrase[0].isalnum() or phrase[0] == "_") else ""
    end_boundary = r"\b" if phrase and (phrase[-1].isalnum() or phrase[-1] == "_") else ""
    return re.compile(f"{start_boundary}{re.escape(phrase)}{end_boundary}", re.IGNORECASE)


def load_phrase_bank(path: str) -> dict[str, int]:
    """
    Load the phrase bank mapping AI-writing phrases to weights from a JSON file.
    
    Args:
        path: Path to the JSON phrase bank file.
        
    Returns:
        A dictionary mapping phrases/constructions to their integer weights.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Phrase bank must be a JSON object mapping strings to integers.")
    return {str(k): int(v) for k, v in data.items()}


def score_phrases(text: str, phrase_bank: dict[str, int]) -> tuple[float, list[dict[str, Any]]]:
    """
    Score the input text based on occurrences of known AI-writing phrases.
    
    Finds all occurrences of phrases and constructions in the input text in a 
    case-insensitive manner, resolves any overlapping matches greedily (prioritizing 
    longer matches and then higher-weight matches), and returns a normalized score 
    and detailed list of matches.
    
    The score is calculated as:
        score = min(40, sum(weights) * (500 / word_count)) if word_count > 0 else 0.0
    
    Args:
        text: The input text to analyze.
        phrase_bank: A dictionary mapping phrases/constructions to weights (1-5).
        
    Returns:
        A tuple containing:
            - The normalized score (float between 0.0 and 40.0).
            - A list of dictionaries, one for each match, in order of occurrence.
              Each dictionary contains:
                - "phrase": The key from the phrase bank.
                - "weight": The weight of the phrase.
                - "position": The starting character index in the text.
                - "context_snippet": A context snippet of up to 30 characters before 
                  and after the match.
    """
    if not text.strip():
        return 0.0, []

    # Count words by splitting on whitespace
    word_count = len(text.split())
    if word_count == 0:
        return 0.0, []

    all_matches: list[MatchInfo] = []

    # Find all matches for each phrase/construction pattern
    for phrase, weight in phrase_bank.items():
        pattern = _compile_pattern(phrase)
        for match in pattern.finditer(text):
            all_matches.append(
                MatchInfo(
                    start=match.start(),
                    end=match.end(),
                    phrase=phrase,
                    weight=weight,
                    matched_text=match.group(0),
                )
            )

    # Sort matches to resolve overlaps greedily:
    # 1. Match length (end - start) descending: prefer longer/more specific phrases
    # 2. Weight descending: prefer higher-weight matches
    # 3. Start index ascending: leftmost first
    all_matches.sort(key=lambda m: (-(m.end - m.start), -m.weight, m.start))

    selected_matches: list[MatchInfo] = []
    for match in all_matches:
        # Check if this match overlaps with any already selected match
        overlap = False
        for sel in selected_matches:
            if match.start < sel.end and sel.start < match.end:
                overlap = True
                break
        if not overlap:
            selected_matches.append(match)

    # Sort selected matches back to original occurrence order in the text
    selected_matches.sort(key=lambda m: m.start)

    # Build the final output list and sum the weights
    matches_list: list[dict[str, Any]] = []
    total_weight = 0

    for m in selected_matches:
        total_weight += m.weight
        
        # Get 30 characters context window
        snippet_start = max(0, m.start - 30)
        snippet_end = min(len(text), m.end + 30)
        context_snippet = text[snippet_start:snippet_end]

        matches_list.append(
            {
                "phrase": m.phrase,
                "weight": m.weight,
                "position": m.start,
                "context_snippet": context_snippet,
            }
        )

    # Calculate normalized score
    score = min(40.0, total_weight * (500.0 / word_count))

    return score, matches_list
