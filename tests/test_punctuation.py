import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.signals.punctuation import score_punctuation

def test_score_punctuation_empty_input():
    score, info = score_punctuation("")
    assert score == 0.0
    assert info == {
        "em_dash_freq": 0.0,
        "colon_led_sentence_freq": 0.0,
        "parenthetical_density": 0.0,
    }

    score, info = score_punctuation("     \n   ")
    assert score == 0.0
    assert info == {
        "em_dash_freq": 0.0,
        "colon_led_sentence_freq": 0.0,
        "parenthetical_density": 0.0,
    }

def test_score_punctuation_no_punctuation():
    score, info = score_punctuation("Hello world this is a test text without any punctuation mark")
    assert score == 0.0
    assert info["em_dash_freq"] == 0.0
    assert info["colon_led_sentence_freq"] == 0.0
    assert info["parenthetical_density"] == 0.0

def test_score_punctuation_baseline_scaling():
    # Construct a text with high punctuation densities to hit the cap
    text = (
        "This is a test—with an em-dash. "
        "Here is a colon: it introduces a list. "
        "This sentence has (some parenthesis) inside."
    )
    score, info = score_punctuation(text)
    
    # We have 3 sentences.
    # Words: "This", "is", "a", "test—with", "an", "em-dash.", "Here", "is", "a", "colon:", "it", "introduces", "a", "list.", "This", "sentence", "has", "(some", "parenthesis)", "inside."
    # Total word count: 20
    # em-dash count: 1 ("—")
    # em-dash freq per 1000w: 1 / 20 * 1000 = 50.0 (baseline: 0.3, ratio = 166.7)
    # colon-led: 1 sentence out of 3 = 0.333 (baseline: 0.05, ratio = 6.67)
    # parenthetical: 1 sentence out of 3 = 0.333 (baseline: 0.05, ratio = 6.67)
    # Average ratio is way over 2.0. So score should be capped at 15.0.
    assert score == 15.0
    assert info["em_dash_freq"] == 50.0
    assert abs(info["colon_led_sentence_freq"] - 0.3333333333333333) < 1e-5
    assert abs(info["parenthetical_density"] - 0.3333333333333333) < 1e-5

def test_score_punctuation_low_density():
    # Construct a text with low punctuation densities to test scaling below the cap
    # We want 1000 words. Let's make it 1000 words with:
    # - 0 em-dashes
    # - 0 colons
    # - 0 parentheses
    text = "word " * 1000
    score, info = score_punctuation(text)
    assert score == 0.0
    assert info["em_dash_freq"] == 0.0
    assert info["colon_led_sentence_freq"] == 0.0
    assert info["parenthetical_density"] == 0.0

def test_score_punctuation_intermediate():
    # Let's construct a text to get an average ratio of exactly 1.0 (so score is 7.5)
    # em_dash_ratio + colon_ratio + parenthesis_ratio = 3.0
    # Let's make:
    # em_dash_freq = 0.3 (so ratio = 1.0)
    # colon_led_sentence_freq = 0.05 (so ratio = 1.0)
    # parenthetical_density = 0.05 (so ratio = 1.0)
    # To do this cleanly:
    # 20 sentences.
    # Each sentence has 10 words. Total 200 words.
    # To get em_dash_freq = 0.3 per 1000 words:
    # For 200 words, we need 0.3 * (200 / 1000) = 0.06 em-dashes.
    # Since we can't have fractional em-dashes, let's just make the math check out with some realistic numbers.
    # Let's say:
    # Word count: 1000 words.
    # sentences: 20 sentences.
    # em-dashes: 0 (ratio = 0)
    # colon sentences: 2 out of 20 = 0.10 (ratio = 2.0)
    # parenthesis sentences: 1 out of 20 = 0.05 (ratio = 1.0)
    # Average ratio = (0 + 2.0 + 1.0) / 3.0 = 1.0
    # Score should be: (1.0 / 2.0) * 15.0 = 7.5
    
    sentences = []
    for i in range(20):
        if i < 2:
            sentences.append("This is a sentence: with a colon.")  # 7 words
        elif i == 2:
            sentences.append("This is a sentence (with parenthesis).")  # 6 words
        else:
            sentences.append("This is a normal sentence.")  # 5 words
            
    text = " ".join(sentences)
    # Total word count: 2 * 7 + 1 * 6 + 17 * 5 = 14 + 6 + 85 = 105 words
    # em-dashes: 0 (freq = 0, ratio = 0)
    # colon sentences: 2 / 20 = 0.10 (ratio = 0.10 / 0.05 = 2.0)
    # parenthesis sentences: 1 / 20 = 0.05 (ratio = 0.05 / 0.05 = 1.0)
    # Average ratio = 1.0
    # Score = 7.5
    
    score, info = score_punctuation(text)
    assert abs(score - 7.5) < 1e-5

def test_score_punctuation_ai_vs_human():
    ai_text = (
        "Moreover, we must delve into the multifaceted complexities of today's fast-paced world: it is changing fast. "
        "Furthermore, it stands as a testament to the transformative power of cutting-edge technology (which is great). "
        "Additionally, we should foster innovation to unlock the potential of these tools -- they are useful."
    )
    human_text = (
        "The cat sat on the mat. The dog sat on the mat. The cat and the dog both sat on the mat."
    )
    ai_score, _ = score_punctuation(ai_text)
    human_score, _ = score_punctuation(human_text)
    assert ai_score > human_score
    assert ai_score > 10.0
    assert human_score == 0.0

