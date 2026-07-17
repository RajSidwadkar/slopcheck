import re
import statistics
from typing import Any

# Common abbreviations that should not trigger sentence boundaries
ABBREVIATIONS = {
    "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "vs", "etc", "st", "co", "inc", "ltd",
    "e.g", "i.e", "u.s", "a.m", "p.m", "b.c", "a.d"
}


def _is_abbreviation(text: str, punct_idx: int) -> bool:
    """Check if the punctuation at punct_idx is part of a common abbreviation."""
    preceding = text[:punct_idx].lower()
    
    for abbr in ABBREVIATIONS:
        if preceding.endswith(abbr):
            start_idx = len(preceding) - len(abbr)
            # Ensure it is a whole word by checking the character before the abbreviation
            if start_idx == 0 or not preceding[start_idx - 1].isalnum():
                return True
    return False


def split_sentences(text: str) -> list[str]:
    """
    Split the input text into a list of sentences.
    
    A naive but robust sentence splitter that breaks text on sentence-ending
    punctuation (.!?) followed by whitespace and a capital letter, avoiding
    splits on common abbreviations like 'Dr.', 'e.g.', 'U.S.', etc.
    
    Args:
        text: The input text to split.
        
    Returns:
        A list of stripped sentence strings.
    """
    if not text.strip():
        return []

    # Match sentence-ending punctuation followed by whitespace and a capital letter
    pattern = re.compile(r"([.!?])(\s+)([A-Z])")
    
    sentences: list[str] = []
    last_idx = 0
    
    for match in pattern.finditer(text):
        punct_idx = match.start(1)
        if _is_abbreviation(text, punct_idx):
            continue
            
        # Split point is right after the punctuation mark
        split_idx = match.end(1)
        sentence = text[last_idx:split_idx].strip()
        if sentence:
            sentences.append(sentence)
        last_idx = split_idx
        
    # Append the remainder of the text
    remaining = text[last_idx:].strip()
    if remaining:
        sentences.append(remaining)
        
    return sentences


def score_rhythm(text: str) -> tuple[float, dict[str, Any]]:
    """
    Score the rhythmic variance of sentence lengths in the input text.
    
    Computes the word count for each sentence and calculates the coefficient 
    of variation (CV = stdev / mean). A lower CV indicates more uniform (potentially 
    AI-generated) sentence lengths, while a higher CV indicates more natural, 
    bursty human-like variation.
    
    The CV is mapped to a 0-20 score:
        - CV <= 0.35 -> 20.0 (maximum suspicion, too uniform)
        - CV >= 0.65 -> 0.0 (low suspicion, human-like variance)
        - In between -> linear interpolation
        
    Args:
        text: The input text to analyze.
        
    Returns:
        A tuple containing:
            - The rhythm score (float between 0.0 and 20.0).
            - A dictionary with keys:
                - "cv": The coefficient of variation.
                - "sentence_count": The number of parsed sentences.
                - "mean_len": The mean sentence length in words.
    """
    sentences = split_sentences(text)
    sentence_count = len(sentences)
    
    # Handle edge case: less than 2 sentences where CV is undefined
    if sentence_count < 2:
        # Calculate mean length of whatever sentences exist
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / sentence_count if sentence_count > 0 else 0.0
        return 0.0, {
            "cv": 0.0,
            "sentence_count": sentence_count,
            "mean_len": mean_len,
        }

    lengths = [len(s.split()) for s in sentences]
    mean_len = statistics.mean(lengths)
    
    # Handle edge case: if mean_len is 0 (all sentences are empty of words)
    if mean_len == 0.0:
        return 0.0, {
            "cv": 0.0,
            "sentence_count": sentence_count,
            "mean_len": 0.0,
        }

    stdev = statistics.stdev(lengths)
    cv = stdev / mean_len

    # Map CV to a 0-20 score
    if cv <= 0.35:
        score = 20.0
    elif cv >= 0.65:
        score = 0.0
    else:
        # Linear interpolation from 20 to 0 between 0.35 and 0.65
        score = 20.0 * (0.65 - cv) / 0.30

    return score, {
        "cv": cv,
        "sentence_count": sentence_count,
        "mean_len": mean_len,
    }
