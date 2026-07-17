import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.signals.lexical import score_lexical

def test_score_lexical_empty_input():
    score, info = score_lexical("")
    assert score == 0.0
    assert info == {
        "ttr": 0.0,
        "unique_words": 0,
        "total_words": 0,
    }

    score, info = score_lexical("     \n   ")
    assert score == 0.0
    assert info == {
        "ttr": 0.0,
        "unique_words": 0,
        "total_words": 0,
    }

def test_score_lexical_punctuation_only():
    score, info = score_lexical("!!! ??? --- ...")
    assert score == 0.0
    assert info == {
        "ttr": 0.0,
        "unique_words": 0,
        "total_words": 0,
    }

def test_score_lexical_all_unique():
    # 5 words, all unique
    text = "The quick brown fox jumps"
    score, info = score_lexical(text)
    assert info["total_words"] == 5
    assert info["unique_words"] == 5
    assert info["ttr"] == 1.0
    assert score == 10.0  # Max score

def test_score_lexical_half_unique():
    # 10 words total, 5 unique (each word repeated twice)
    text = "hello world hello world hello world hello world hello world"
    score, info = score_lexical(text)
    assert info["total_words"] == 10
    assert info["unique_words"] == 2  # wait: "hello" and "world" are the only unique words
    assert info["ttr"] == 0.2
    assert abs(score - 2.0) < 1e-5

def test_score_lexical_punctuation_stripping():
    # Punctuation should be stripped and words normalized
    text = "Hello, hello! World... world."
    score, info = score_lexical(text)
    # Normalized: ["hello", "hello", "world", "world"]
    assert info["total_words"] == 4
    assert info["unique_words"] == 2
    assert info["ttr"] == 0.5
    assert abs(score - 5.0) < 1e-5

def test_score_lexical_ai_vs_human():
    ai_text = (
        "Moreover, we must delve into the multifaceted complexities of today's fast-paced world: it is changing fast. "
        "Furthermore, it stands as a testament to the transformative power of cutting-edge technology (which is great). "
        "Additionally, we should foster innovation to unlock the potential of these tools -- they are useful."
    )
    human_text = (
        "The cat sat on the mat. The dog sat on the mat. The cat and the dog both sat on the mat."
    )
    ai_score, _ = score_lexical(ai_text)
    human_score, _ = score_lexical(human_text)
    assert ai_score > human_score
    assert (ai_score - human_score) > 2.0

