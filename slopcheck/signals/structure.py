import re
import statistics
from typing import Any


def score_structure(text: str) -> tuple[float, dict[str, Any]]:
    """
    Score the structural uniformity of paragraph lengths in the input text.
    
    Splits the text into paragraphs separated by blank lines and computes the 
    standard deviation of paragraph word counts. A low standard deviation 
    indicates uniform (potentially AI-generated) paragraph lengths, which 
    results in a high score (up to 15.0).
    
    The score is mapped as follows:
        - stdev == 0.0 -> 15.0 (maximum uniformity/suspicion)
        - stdev >= 20.0 -> 0.0 (high variance/human-like)
        - 0.0 < stdev < 20.0 -> linear interpolation
        
    If the text has fewer than 2 paragraphs, uniformity cannot be measured. 
    In this case, the function gracefully returns a score of 0.0.
    
    Args:
        text: The input text to analyze.
        
    Returns:
        A tuple containing:
            - The structure score (float between 0.0 and 15.0).
            - A dictionary with raw metrics:
                - "stdev": The standard deviation of paragraph word counts.
                - "paragraph_count": The number of parsed paragraphs.
                - "mean_len": The mean paragraph length in words.
    """
    if not text.strip():
        return 0.0, {
            "stdev": 0.0,
            "paragraph_count": 0,
            "mean_len": 0.0,
        }

    # Split into paragraphs by finding blank lines (double newlines or lines with only whitespace)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paragraph_count = len(paragraphs)

    # Word counts per paragraph
    lengths = [len(p.split()) for p in paragraphs]
    mean_len = sum(lengths) / paragraph_count if paragraph_count > 0 else 0.0

    # Must handle single-paragraph input gracefully by returning 0.0
    if paragraph_count < 2:
        return 0.0, {
            "stdev": 0.0,
            "paragraph_count": paragraph_count,
            "mean_len": mean_len,
        }

    stdev = statistics.stdev(lengths)

    # Map stdev to 0-15 score: low stdev (uniform) -> high score
    if stdev <= 0.0:
        score = 15.0
    elif stdev >= 20.0:
        score = 0.0
    else:
        score = 15.0 * (20.0 - stdev) / 20.0

    return score, {
        "stdev": stdev,
        "paragraph_count": paragraph_count,
        "mean_len": mean_len,
    }
