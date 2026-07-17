import re
from typing import Any
from slopcheck.signals.rhythm import split_sentences


def score_punctuation(text: str) -> tuple[float, dict[str, Any]]:
    """
    Score the frequency of specific punctuation markers associated with AI-writing.
    
    Measures:
        1. em-dash frequency per 1000 words (baseline: 0.3 per 1000 words).
        2. colon-led sentence frequency (fraction of sentences containing colons, baseline: 0.05).
        3. parenthetical-aside density (fraction of sentences containing parentheses, baseline: 0.05).
        
    The overall ratio-to-baseline is computed as the average of these three ratios.
    The score scales from 0.0 to 15.0 as the ratio-to-baseline increases from 0.0 to 2.0,
    and is capped at exactly 15.0 for any ratio past 2.0 (2x baseline).
    
    Args:
        text: The input text to analyze.
        
    Returns:
        A tuple containing:
            - The punctuation score (float between 0.0 and 15.0).
            - A dictionary containing the raw metrics:
                - "em_dash_freq": The em-dash frequency per 1000 words.
                - "colon_led_sentence_freq": The fraction of sentences with a colon.
                - "parenthetical_density": The fraction of sentences with parentheses.
    """
    # Define baselines
    em_dash_baseline = 0.3
    colon_baseline = 0.05
    parenthesis_baseline = 0.05

    # Early exit for empty or whitespace-only inputs
    if not text.strip():
        return 0.0, {
            "em_dash_freq": 0.0,
            "colon_led_sentence_freq": 0.0,
            "parenthetical_density": 0.0,
        }

    # Word count
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        return 0.0, {
            "em_dash_freq": 0.0,
            "colon_led_sentence_freq": 0.0,
            "parenthetical_density": 0.0,
        }

    # Count em-dashes (both Unicode em-dash and double hyphen '--')
    em_dash_count = text.count("—") + text.count("--")
    em_dash_freq = (em_dash_count / word_count) * 1000.0

    # Parse sentences
    sentences = split_sentences(text)
    sentence_count = len(sentences)

    if sentence_count == 0:
        return 0.0, {
            "em_dash_freq": em_dash_freq,
            "colon_led_sentence_freq": 0.0,
            "parenthetical_density": 0.0,
        }

    # Count sentences containing a colon (colon-led sentences)
    colon_sentence_count = sum(1 for s in sentences if ":" in s)
    colon_led_sentence_freq = colon_sentence_count / sentence_count

    # Count sentences containing parentheses (parenthetical-asides)
    parenthesis_sentence_count = sum(1 for s in sentences if "(" in s and ")" in s)
    parenthetical_density = parenthesis_sentence_count / sentence_count

    # Calculate ratios to baseline
    em_dash_ratio = em_dash_freq / em_dash_baseline
    colon_ratio = colon_led_sentence_freq / colon_baseline
    parenthesis_ratio = parenthetical_density / parenthesis_baseline

    # Combined ratio (average of the three ratios)
    overall_ratio = (em_dash_ratio + colon_ratio + parenthesis_ratio) / 3.0

    # Score scales 0-15 as ratio increases from 0x to 2x (capped at 15.0 past 2x)
    if overall_ratio >= 2.0:
        score = 15.0
    else:
        score = (overall_ratio / 2.0) * 15.0

    return score, {
        "em_dash_freq": em_dash_freq,
        "colon_led_sentence_freq": colon_led_sentence_freq,
        "parenthetical_density": parenthetical_density,
    }
