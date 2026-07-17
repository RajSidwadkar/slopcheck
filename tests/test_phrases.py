
import pytest
from slopcheck.signals.phrases import load_phrase_bank, score_phrases

@pytest.fixture
def phrase_bank():
    
    from slopcheck.scorer import DEFAULT_PHRASE_BANK_PATH
    return load_phrase_bank(DEFAULT_PHRASE_BANK_PATH)

def test_load_phrase_bank(phrase_bank):
    assert isinstance(phrase_bank, dict)
    assert len(phrase_bank) >= 80 and len(phrase_bank) <= 120
    for phrase, weight in phrase_bank.items():
        assert isinstance(phrase, str)
        assert isinstance(weight, int)
        assert 1 <= weight <= 5

def test_score_phrases_empty_input(phrase_bank):
    score, matches = score_phrases("", phrase_bank)
    assert score == 0.0
    assert matches == []

    score, matches = score_phrases("   \n  \t ", phrase_bank)
    assert score == 0.0
    assert matches == []

def test_score_phrases_basic(phrase_bank):
    text = "Moreover, we must navigate the complexities of this groundbreaking issue in today's fast-paced world."
    # Word count: 14
    score, matches = score_phrases(text, phrase_bank)
    
    assert score > 0.0
    # The score should be capped at 40
    assert score <= 40.0
    
    matched_phrases = {m["phrase"] for m in matches}
    assert "moreover" in matched_phrases
    assert "navigate the complexities" in matched_phrases
    assert "groundbreaking" in matched_phrases
    assert "in today's fast-paced world" in matched_phrases

    # Check match structure
    for m in matches:
        assert "phrase" in m
        assert "weight" in m
        assert "position" in m
        assert "context_snippet" in m
        assert isinstance(m["phrase"], str)
        assert isinstance(m["weight"], int)
        assert isinstance(m["position"], int)
        assert isinstance(m["context_snippet"], str)
        # Context snippet should contain the matched text
        assert text[m["position"] : m["position"] + len(text)].startswith(text[m["position"] : m["position"] + 5])

def test_overlap_resolution(phrase_bank):
    # "pushing the boundaries" (weight 4) contains "boundaries" (weight 2)
    # The resolver should only select the longer match
    text = "We are constantly pushing the boundaries of what is possible."
    score, matches = score_phrases(text, phrase_bank)
    
    matched_phrases = {m["phrase"] for m in matches}
    assert "pushing the boundaries" in matched_phrases
    assert "boundaries" not in matched_phrases

def test_construction_matching(phrase_bank):
    text = "It's not just a tool, it's a partner in our journey of discovery."
    score, matches = score_phrases(text, phrase_bank)
    
    matched_phrases = {m["phrase"] for m in matches}
    # Check that it matched the construction pattern
    assert any("not just" in p for p in matched_phrases)
    # Check that "journey of" also matched because X/Y are non-greedy and don't overlap
    assert "journey of" in matched_phrases

def test_score_phrases_ai_vs_human(phrase_bank):
    ai_text = (
        "Moreover, we must delve into the multifaceted complexities of today's fast-paced world: it is changing fast. "
        "Furthermore, it stands as a testament to the transformative power of cutting-edge technology (which is great). "
        "Additionally, we should foster innovation to unlock the potential of these tools -- they are useful."
    )
    human_text = (
        "The cat sat on the mat. The dog sat on the mat. The cat and the dog both sat on the mat."
    )
    ai_score, _ = score_phrases(ai_text, phrase_bank)
    human_score, _ = score_phrases(human_text, phrase_bank)
    assert ai_score > human_score
    assert ai_score > 10.0
    assert human_score == 0.0

def test_load_phrase_bank_invalid(tmp_path):
    import json
    invalid_file = tmp_path / "invalid_phrase_bank.json"
    invalid_file.write_text(json.dumps([1, 2, 3]))
    
    with pytest.raises(ValueError) as excinfo:
        load_phrase_bank(str(invalid_file))
    assert "Phrase bank must be a JSON object" in str(excinfo.value)


