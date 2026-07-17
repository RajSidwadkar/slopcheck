import string
from typing import Any


def score_lexical(text: str) -> tuple[float, dict[str, Any]]:
    """
    Score the lexical diversity of the input text using the Type-Token Ratio (TTR).
    
    TTR is computed as the number of unique words divided by the total number of words,
    after lowercasing and stripping punctuation. A higher TTR indicates more lexical 
    diversity (human-like) and scales the score from 0.0 to 10.0.
    
    Args:
        text: The input text to analyze.
        
    Returns:
        A tuple containing:
            - The lexical score (float between 0.0 and 10.0).
            - A dictionary with raw metrics:
                - "ttr": The Type-Token Ratio (float).
                - "unique_words": The count of unique cleaned words (int).
                - "total_words": The count of total cleaned words (int).
    """
    # Early check for empty or whitespace-only text
    if not text.strip():
        return 0.0, {
            "ttr": 0.0,
            "unique_words": 0,
            "total_words": 0,
        }

    # Split words, strip punctuation, and convert to lowercase
    words = text.split()
    cleaned_words: list[str] = []
    
    for w in words:
        # Strip all standard punctuation characters
        cleaned = w.strip(string.punctuation).lower()
        if cleaned:
            cleaned_words.append(cleaned)

    total_words = len(cleaned_words)

    # Handle edge cases (empty text, strings with only punctuation)
    if total_words == 0:
        return 0.0, {
            "ttr": 0.0,
            "unique_words": 0,
            "total_words": 0,
        }

    unique_words_set = set(cleaned_words)
    unique_words = len(unique_words_set)
    ttr = unique_words / total_words

    # Score scales 0-10 based on TTR (capped at exactly 10.0)
    score = min(10.0, ttr * 10.0)

    return score, {
        "ttr": ttr,
        "unique_words": unique_words,
        "total_words": total_words,
    }
