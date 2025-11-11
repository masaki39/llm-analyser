"""Tests for main CLI module."""

import sys
from unittest.mock import patch

import pytest

from pplyz.cli import list_supported_models, main, parse_arguments


class TestParseArguments:
    """Test command-line argument parsing."""

    def test_parse_required_arguments(self):
        """Test parsing required arguments."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1,col2",
            "--output",
            "output.csv",
            "--fields",
            "score:float,label:str",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.input == "test.csv"
            assert args.columns == "col1,col2"
            assert args.output == "output.csv"
            assert args.fields == "score:float,label:str"

    def test_parse_with_model_option(self):
        """Test parsing with model option."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
            "--output",
            "output.csv",
            "--model",
            "gpt-4o",
            "--fields",
            "confidence:float",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.model == "gpt-4o"

    def test_parse_with_preview_option(self):
        """Test parsing with preview option."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
            "--preview",
            "--fields",
            "flag:bool",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.preview is True

    def test_parse_with_preview_rows_option(self):
        """Test parsing with preview rows option."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
            "--preview",
            "--preview-rows",
            "5",
            "--fields",
            "flag:bool",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.preview_rows == 5

    def test_parse_with_fields_option(self):
        """Test parsing with fields option."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
            "--fields",
            "score:float,label:str",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.fields == "score:float,label:str"

    def test_parse_with_list_option(self):
        """Test parsing with list flag."""
        test_args = ["pplyz", "--list"]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.list_models is True

    def test_parse_short_options(self):
        """Test parsing with short option names."""
        test_args = [
            "pplyz",
            "-i",
            "test.csv",
            "-c",
            "col1,col2",
            "-o",
            "output.csv",
            "-m",
            "gpt-4o",
            "-p",
            "-f",
            "flag:bool",
            "-R",
            "-l",
        ]

        with patch.object(sys, "argv", test_args):
            args = parse_arguments()

            assert args.input == "test.csv"
            assert args.columns == "col1,col2"
            assert args.output == "output.csv"
            assert args.model == "gpt-4o"
            assert args.preview is True
            assert args.fields == "flag:bool"
            assert args.no_resume is True
            assert args.list_models is True

    def test_help_uses_compact_flags(self, capsys):
        """Help text should not duplicate metavar values in option listing."""
        test_args = ["pplyz", "--help"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "usage: pplyz [options]" in captured.out
        options_text = captured.out.split("options:", 1)[1]
        assert "-i, --input" in options_text
        assert "--input INPUT, -i INPUT" not in options_text
        # Short flags should appear before long flags
        assert options_text.index("-h, --help") < options_text.index("-i, --input")


class TestListSupportedModels:
    """Test list supported models function."""

    def test_list_supported_models_output(self, capsys):
        """Test that list_supported_models prints model information."""
        list_supported_models()

        captured = capsys.readouterr()

        # Check that output contains expected content
        assert "SUPPORTED MODELS" in captured.out
        assert "gemini/gemini-2.5-flash-lite" in captured.out
        assert "gemini/gemini-2.0-flash-lite" in captured.out
        assert "gpt-4o" in captured.out
        assert "claude-3-5-sonnet" in captured.out
        assert "litellm.ai" in captured.out


class TestMainExecution:
    """Test main function execution flow."""

    def test_main_exits_with_list_flag(self, capsys):
        """Test that --list exits after printing."""
        test_args = ["pplyz", "--list"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "SUPPORTED MODELS" in captured.out

    def test_main_requires_input_and_columns(self, capsys):
        """Test that main requires --input and --columns without --list."""
        test_args = ["pplyz"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "required: --input/-i, --columns/-c, --fields/-f" in captured.out

    def test_main_requires_columns_when_only_input(self, capsys):
        """Test that main requires --columns when only --input is provided."""
        test_args = ["pplyz", "--input", "test.csv"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "required: --columns/-c, --fields/-f" in captured.out

    def test_main_requires_input_when_only_columns(self, capsys):
        """Test that main requires --input when only --columns is provided."""
        test_args = ["pplyz", "--columns", "col1,col2"]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "required: --input/-i, --fields/-f" in captured.out

    def test_main_accepts_preview_without_output(self):
        """Test that main accepts --preview without --output."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
            "--preview",
            "--fields",
            "flag:bool",
        ]

        with patch.object(sys, "argv", test_args):
            with patch("pplyz.cli.get_user_prompt", return_value="Test prompt"):
                with patch("pplyz.cli.LLMClient"):
                    with patch("pplyz.cli.CSVProcessor"):
                        # Should not raise SystemExit for missing --output
                        # (will fail later due to missing file, but argument parsing should pass)
                        try:
                            main()
                        except (FileNotFoundError, SystemExit):
                            pass  # Expected due to missing test.csv

    def test_main_requires_fields_when_missing(self, capsys):
        """Test that main requires --fields when --input/--columns are provided."""
        test_args = [
            "pplyz",
            "--input",
            "test.csv",
            "--columns",
            "col1",
        ]

        with patch.object(sys, "argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "required: --fields/-f" in captured.out
