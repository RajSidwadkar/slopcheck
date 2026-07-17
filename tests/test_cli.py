import os
import sys
from unittest.mock import patch, MagicMock
import pytest

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

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
        assert "Slopcheck Analysis Report" in captured.out
        assert "Total Score" in captured.out


def test_cli_read_from_stdin(capsys):
    # Mock sys.stdin.read to return some text
    stdin_content = "This is a normal sentence."
    with patch("sys.argv", ["slopcheck", "-"]):
        with patch("sys.stdin.read", return_value=stdin_content):
            with pytest.raises(SystemExit) as excinfo:
                main()
            assert excinfo.value.code == 0
            
            captured = capsys.readouterr()
            assert "Slopcheck Analysis Report" in captured.out


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
        assert "Matched AI-Writing Phrases:" in captured.out
        assert "Line 1" in captured.out


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
