import os
import sys
import json

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from slopcheck.render import print_json, print_report

@pytest.fixture
def sample_result():
    return {
        "total_score": 78.4,
        "risk_band": "high",
        "_filename": "example.txt",
        "_text": "Moreover, we must navigate the complexities.\n\nIt is important.",
        "signals": {
            "phrases": {
                "score": 32.0,
                "matches": [
                    {
                        "phrase": "moreover",
                        "weight": 3,
                        "position": 0,
                        "context_snippet": "Moreover, we must navigate the",
                    }
                ],
            },
            "rhythm": {"score": 18.0, "detail": {}},
            "punctuation": {"score": 12.0, "detail": {}},
            "structure": {"score": 9.0, "detail": {}},
            "lexical": {"score": 7.0, "detail": {}},
        },
    }

def test_print_json(sample_result, capsys):
    print_json(sample_result)
    captured = capsys.readouterr()
    
    # Assert output is valid JSON
    data = json.loads(captured.out)
    assert data["total_score"] == 78.4
    assert data["risk_band"] == "high"
    # Internal metadata keys should be filtered out
    assert "_filename" not in data
    assert "_text" not in data

def test_print_report_no_color_no_explain(sample_result, capsys):
    print_report(sample_result, explain=False, color=False)
    captured = capsys.readouterr()
    output = captured.out
    
    # Verify exact shape and headers
    assert "slopcheck: example.txt" in output
    assert "Score: 78/100  (high AI-signal density)" in output
    assert "Phrase matches        32/40" in output
    assert "Sentence rhythm       18/20" in output
    assert "Punctuation           12/15" in output
    assert "Paragraph uniformity   9/15" in output
    assert "Lexical diversity      7/10" in output
    
    # Explain block should be omitted
    assert "Flagged spans:" not in output
    
    # Warning/Disclaimer should be present
    assert "⚠ Heuristic estimate, not proof. False positives common in formal/corporate writing" in output
    assert "and non-native English styles." in output
    
    # No ANSI escape sequences should exist
    assert "\033[" not in output

def test_print_report_with_explain(sample_result, capsys):
    print_report(sample_result, explain=True, color=False)
    captured = capsys.readouterr()
    output = captured.out
    
    # Flagged spans and context snippet should be visible
    assert "Flagged spans:" in output
    assert 'L1: "...Moreover, we must navigate the..."' in output

def test_print_report_with_color(sample_result, capsys):
    print_report(sample_result, explain=False, color=True)
    captured = capsys.readouterr()
    output = captured.out
    
    # ANSI escape sequences for coloring should be present
    assert "\033[" in output
    # Specifically check for Red code (\033[31m) for high risk
    assert "\033[31m" in output

def test_render_empty_input(capsys):
    from slopcheck.scorer import analyze
    empty_result = analyze("")
    
    # Test print_json
    print_json(empty_result)
    captured_json = capsys.readouterr()
    assert "total_score" in captured_json.out
    
    # Test print_report
    print_report(empty_result, explain=True, color=False)
    captured_report = capsys.readouterr()
    assert "Score: 0/100" in captured_report.out

def test_render_ai_vs_human(capsys):
    from slopcheck.scorer import analyze
    ai_text = (
        "Moreover, we must delve into the multifaceted complexities of today's fast-paced world: it is changing fast. "
        "Furthermore, it stands as a testament to the transformative power of cutting-edge technology (which is great). "
        "Additionally, we should foster innovation to unlock the potential of these tools -- they are useful."
    )
    human_text = (
        "The cat sat on the mat. The dog sat on the mat. The cat and the dog both sat on the mat."
    )
    
    ai_res = analyze(ai_text)
    human_res = analyze(human_text)
    
    print_report(ai_res, explain=False, color=False)
    ai_out = capsys.readouterr().out
    
    print_report(human_res, explain=False, color=False)
    human_out = capsys.readouterr().out
    
    # Find the scores in the reports
    # AI report should print a high score
    assert "Score:" in ai_out
    assert "Score:" in human_out
    
    # Simple extraction of score numbers
    import re
    ai_score_val = float(re.search(r"Score:\s+(\d+)/100", ai_out).group(1))
    human_score_val = float(re.search(r"Score:\s+(\d+)/100", human_out).group(1))
    
    assert ai_score_val > human_score_val

def test_print_report_encoding_error(sample_result):
    from unittest.mock import patch, MagicMock
    mock_stdout = MagicMock()
    mock_stdout.encoding = "ascii"
    mock_stdout.write = MagicMock()
    
    with patch("sys.stdout", mock_stdout):
        print_report(sample_result, explain=False, color=False)
        
    written = "".join(call[0][0] for call in mock_stdout.write.call_args_list)
    assert "[!]" in written


