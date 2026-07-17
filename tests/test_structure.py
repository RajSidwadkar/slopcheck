import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.signals.structure import score_structure

def test_score_structure_empty_input():
    score, info = score_structure("")
    assert score == 0.0
    assert info == {
        "stdev": 0.0,
        "paragraph_count": 0,
        "mean_len": 0.0,
    }

    score, info = score_structure("     \n\n   ")
    assert score == 0.0
    assert info == {
        "stdev": 0.0,
        "paragraph_count": 0,
        "mean_len": 0.0,
    }

def test_score_structure_single_paragraph():
    score, info = score_structure("This is a single paragraph. It contains some words.")
    assert score == 0.0
    assert info["stdev"] == 0.0
    assert info["paragraph_count"] == 1
    assert info["mean_len"] == 9.0

def test_score_structure_fully_uniform():
    # Two paragraphs of exactly equal word lengths (5 words each)
    text = "Para one has five words.\n\nPara two has five words."
    score, info = score_structure(text)
    assert info["stdev"] == 0.0
    assert info["paragraph_count"] == 2
    assert info["mean_len"] == 5.0
    assert score == 15.0  # Max uniformity

def test_score_structure_highly_variable():
    # Two paragraphs with large difference in length
    # Para 1: 5 words
    # Para 2: 45 words
    # stdev will be statistics.stdev([5, 45]) = 28.28 > 20.0
    p1 = "word " * 5
    p2 = "word " * 45
    text = f"{p1}\n\n{p2}"
    score, info = score_structure(text)
    assert info["stdev"] > 20.0
    assert score == 0.0  # High variance/human-like

def test_score_structure_intermediate():
    # Two paragraphs with stdev = 10.0 (so score is 7.5)
    # Let's say: lengths are x and y
    # mean = (x + y) / 2
    # stdev = sqrt(((x - mean)^2 + (y - mean)^2) / 1) = abs(x - y) / sqrt(2)
    # If stdev = 10.0:
    # abs(x - y) = 10.0 * sqrt(2) = 14.142
    # Let's use paragraph lengths [10, 24.1421356]
    # More simply, let's use:
    # lengths = [10, 10 + 10 * sqrt(2)] -> diff = 10 * sqrt(2), so stdev = 10.0
    # Let's construct a string with:
    # Para 1: 10 words
    # Para 2: 24 words (diff is 14, so stdev = 14 / 1.4142 = 9.899)
    p1 = "word " * 10
    p2 = "word " * 24
    text = f"{p1}\n\n{p2}"
    score, info = score_structure(text)
    assert abs(info["stdev"] - 9.89949493) < 1e-5
    # score = 15.0 * (20.0 - 9.89949493) / 20.0 = 7.5753788
    assert abs(score - 7.5753788) < 1e-5
