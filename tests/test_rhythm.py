import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.signals.rhythm import split_sentences, score_rhythm

def test_split_sentences_basic():
    text = "Hello world. This is a sentence! Is it really?"
    sentences = split_sentences(text)
    assert sentences == ["Hello world.", "This is a sentence!", "Is it really?"]

def test_split_sentences_abbreviations():
    text = "I saw Dr. Smith at the park. He was with Mr. Jones. The U.S. is large."
    sentences = split_sentences(text)
    assert sentences == [
        "I saw Dr. Smith at the park.",
        "He was with Mr. Jones.",
        "The U.S. is large."
    ]

def test_split_sentences_abbreviations_no_false_negatives():
    # If the abbreviation is at the end of the text
    text = "We arrived at 10 a.m."
    sentences = split_sentences(text)
    assert sentences == ["We arrived at 10 a.m."]

def test_score_rhythm_edge_cases():
    # Empty string
    score, info = score_rhythm("")
    assert score == 0.0
    assert info["sentence_count"] == 0
    assert info["cv"] == 0.0
    assert info["mean_len"] == 0.0

    # One sentence
    score, info = score_rhythm("This is a single sentence.")
    assert score == 0.0
    assert info["sentence_count"] == 1
    assert info["cv"] == 0.0
    assert info["mean_len"] == 5.0

def test_score_rhythm_uniform():
    # Fully uniform (all sentences have same word count)
    text = "This is a sentence. That is a sentence. Here is a sentence."
    # Lengths: [4, 4, 4], mean: 4, stdev: 0.0, cv: 0.0
    score, info = score_rhythm(text)
    assert info["cv"] == 0.0
    assert score == 20.0  # Max suspicion since CV <= 0.35

def test_score_rhythm_bursty():
    # Bursty sentences (large variation in word counts)
    text = "Go. This is a very long sentence with many words. Yes."
    # Lengths: [1, 10, 1], mean: 4, stdev: 5.196, cv: 1.3
    score, info = score_rhythm(text)
    assert info["cv"] > 0.65
    assert score == 0.0  # Low suspicion

def test_score_rhythm_interpolation():
    # Test linear interpolation range
    # Let's construct sentence lengths to have CV around 0.5
    # e.g., lengths = [10, 15, 20]
    # mean = 15
    # stdev = 5
    # cv = 5 / 15 = 0.3333333333333333 -> CV <= 0.35 -> 20.0
    # Let's try: lengths = [10, 20, 30]
    # mean = 20
    # stdev = 10
    # cv = 10 / 20 = 0.5
    # score = 20.0 * (0.65 - 0.5) / 0.30 = 10.0
    text = (
        "Word word word word word word word word word word. "  # 10 words
        "Word word word word word word word word word word word word word word word word word word word word. "  # 20 words
        "Word word word word word word word word word word word word word word word word word word word word word word word word word word word word word word."  # 30 words
    )
    score, info = score_rhythm(text)
    assert abs(info["cv"] - 0.5) < 1e-5
    assert abs(score - 10.0) < 1e-5
