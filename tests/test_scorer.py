import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.scorer import analyze, DEFAULT_PHRASE_BANK_PATH

def test_default_phrase_bank_exists():
    assert os.path.exists(DEFAULT_PHRASE_BANK_PATH), f"Phrase bank not found at {DEFAULT_PHRASE_BANK_PATH}"

def test_analyze_empty_input():
    result = analyze("")
    assert result["total_score"] == 0.0
    assert result["risk_band"] == "low"
    assert "signals" in result
    for signal_name in ["phrases", "rhythm", "punctuation", "structure", "lexical"]:
        assert signal_name in result["signals"]
        assert result["signals"][signal_name]["score"] == 0.0

def test_analyze_structure_and_keys():
    text = (
        "Moreover, we must navigate the complexities of this groundbreaking issue in today's fast-paced world.\n\n"
        "It's not just a tool, it's a partner in our journey of discovery. "
        "This is a second sentence: to check the colon, and also a (parenthesis)."
    )
    result = analyze(text)
    
    assert "total_score" in result
    assert "risk_band" in result
    assert "signals" in result
    
    signals = result["signals"]
    assert "phrases" in signals and "score" in signals["phrases"] and "matches" in signals["phrases"]
    assert "rhythm" in signals and "score" in signals["rhythm"] and "detail" in signals["rhythm"]
    assert "punctuation" in signals and "score" in signals["punctuation"] and "detail" in signals["punctuation"]
    assert "structure" in signals and "score" in signals["structure"] and "detail" in signals["structure"]
    assert "lexical" in signals and "score" in signals["lexical"] and "detail" in signals["lexical"]

def test_risk_bands():
    # Low score
    res_low = analyze("This is a totally normal human sentence with no slop.")
    assert res_low["total_score"] < 35.0
    assert res_low["risk_band"] == "low"

    # High score (force high scores across all indicators)
    high_text = (
        "Moreover: we must navigate the complexities (of life).\n\n"
        "Furthermore: it stands as a testament (to that)."
    )
    res_high = analyze(high_text)
    assert res_high["total_score"] >= 35.0  # Should be medium or high

def test_analyze_ai_vs_human():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    with open(os.path.join(fixtures_dir, "sample_ai.txt"), "r", encoding="utf-8") as f:
        ai_text = f.read()
    with open(os.path.join(fixtures_dir, "sample_human.txt"), "r", encoding="utf-8") as f:
        human_text = f.read()
        
    ai_result = analyze(ai_text)
    human_result = analyze(human_text)
    
    assert ai_result["total_score"] > human_result["total_score"]
    assert ai_result["total_score"] > 80.0
    assert human_result["total_score"] < 20.0
    assert ai_result["risk_band"] == "high"
    assert human_result["risk_band"] == "low"

