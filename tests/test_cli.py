import os
from unittest.mock import patch
import pytest

from slopcheck.cli import main


def test_cli_file_not_found():
    # Mock sys.argv to run with a non-existent file
    with patch("sys.argv", ["slopcheck", "non_existent_file.txt"]):
        with patch("sys.stderr.write") as mock_stderr:
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 2
            mock_stderr.assert_any_call("Error: File not found: non_existent_file.txt\n")


def test_cli_read_from_file(tmp_path, capsys):
    # Create a temporary file
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("Moreover, we must navigate the complexities of this issue.")
    
    with patch("sys.argv", ["slopcheck", str(temp_file)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        
        captured = capsys.readouterr()
        assert "slopcheck: " in captured.out
        assert "Score: " in captured.out


def test_cli_read_from_stdin(capsys):
    # Mock sys.stdin.read to return some text
    stdin_content = "This is a normal sentence."
    with patch("sys.argv", ["slopcheck", "-"]):
        with patch("sys.stdin.read", return_value=stdin_content):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            
            captured = capsys.readouterr()
            assert "slopcheck: stdin" in captured.out


def test_cli_json_output(tmp_path, capsys):
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("Hello world.")
    
    with patch("sys.argv", ["slopcheck", str(temp_file), "--json"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        
        captured = capsys.readouterr()
        # Verify it is valid JSON and has required keys
        import json
        result = json.loads(captured.out)
        assert "total_score" in result
        assert "risk_band" in result


def test_cli_explain_output(tmp_path, capsys):
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("Moreover, we must navigate the complexities.")
    
    # Run with explain
    with patch("sys.argv", ["slopcheck", str(temp_file), "--explain"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        
        captured = capsys.readouterr()
        assert "Flagged spans:" in captured.out
        assert "L1:" in captured.out


def test_cli_high_risk_exit_code(tmp_path):
    # Build text to trigger high risk (score >= 70)
    # We repeat uniform sentences, colons, parentheses, and AI phrases.
    text = (
        "Moreover: we must navigate the complexities (of life).\n\n"
        "Furthermore: it stands as a testament (to that).\n\n"
        "Additionally: it is important to remember (this fact)."
    )
    temp_file = tmp_path / "test_high.txt"
    temp_file.write_text(text)
    
    with patch("sys.argv", ["slopcheck", str(temp_file)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        # Exit code should be 1 since risk_band is high
        assert excinfo.value.code == 1

def test_cli_empty_input(tmp_path, capsys):
    temp_file = tmp_path / "empty.txt"
    temp_file.write_text("")
    
    with patch("sys.argv", ["slopcheck", str(temp_file)]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        captured = capsys.readouterr()
        assert "Score: 0/100" in captured.out

def test_cli_ai_vs_human(capsys):
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    ai_file = os.path.join(fixtures_dir, "sample_ai.txt")
    human_file = os.path.join(fixtures_dir, "sample_human.txt")
    
    # Run on AI file
    with patch("sys.argv", ["slopcheck", ai_file]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        # Should exit with 1 because risk_band is high
        assert excinfo.value.code == 1
        
    ai_captured = capsys.readouterr().out
    
    # Run on Human file
    with patch("sys.argv", ["slopcheck", human_file]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        # Should exit with 0 because risk_band is low
        assert excinfo.value.code == 0
        
    human_captured = capsys.readouterr().out
    
    import re
    ai_score_val = float(re.search(r"Score:\s+(\d+)/100", ai_captured).group(1))
    human_score_val = float(re.search(r"Score:\s+(\d+)/100", human_captured).group(1))
    
    assert ai_score_val > human_score_val
    assert ai_score_val > 80.0
    assert human_score_val < 20.0

def test_cli_read_error():
    with patch("sys.argv", ["slopcheck", "dummy.txt"]):
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("sys.stderr.write") as mock_stderr:
                with pytest.raises(SystemExit) as excinfo:
                    main()
                assert excinfo.value.code == 2
                mock_stderr.assert_any_call("Error reading file: Permission denied\n")

def test_cli_analysis_error(tmp_path):
    temp_file = tmp_path / "dummy.txt"
    temp_file.write_text("dummy content")
    with patch("sys.argv", ["slopcheck", str(temp_file)]):
        with patch("slopcheck.cli.analyze", side_effect=ValueError("Analysis failed")):
            with patch("sys.stderr.write") as mock_stderr:
                with pytest.raises(SystemExit) as excinfo:
                    main()
                assert excinfo.value.code == 2
                mock_stderr.assert_any_call("Error during analysis: Analysis failed\n")


