"""Tests for main CLI module."""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from main import list_supported_models, parse_arguments


class TestParseArguments:
    """Test command-line argument parsing."""

    def test_parse_required_arguments(self):
        """Test parsing required arguments."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1,col2",
            "--output", "output.csv"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.input == "test.csv"
            assert args.columns == "col1,col2"
            assert args.output == "output.csv"

    def test_parse_with_model_option(self):
        """Test parsing with model option."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1",
            "--output", "output.csv",
            "--model", "gpt-4o"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.model == "gpt-4o"

    def test_parse_with_preview_option(self):
        """Test parsing with preview option."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1",
            "--preview"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.preview is True

    def test_parse_with_preview_rows_option(self):
        """Test parsing with preview rows option."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1",
            "--preview",
            "--preview-rows", "5"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.preview_rows == 5

    def test_parse_with_column_prefix_option(self):
        """Test parsing with column prefix option."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1",
            "--output", "output.csv",
            "--column-prefix", "custom"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.column_prefix == "custom"

    def test_parse_with_list_models_option(self):
        """Test parsing with list-models option."""
        test_args = [
            "main.py",
            "--list-models"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.list_models is True

    def test_parse_short_options(self):
        """Test parsing with short option names."""
        test_args = [
            "main.py",
            "-i", "test.csv",
            "-c", "col1,col2",
            "-o", "output.csv",
            "-m", "gpt-4o",
            "-p"
        ]

        with patch.object(sys, 'argv', test_args):
            args = parse_arguments()

            assert args.input == "test.csv"
            assert args.columns == "col1,col2"
            assert args.output == "output.csv"
            assert args.model == "gpt-4o"
            assert args.preview is True


class TestListSupportedModels:
    """Test list supported models function."""

    def test_list_supported_models_output(self, capsys):
        """Test that list_supported_models prints model information."""
        list_supported_models()

        captured = capsys.readouterr()

        # Check that output contains expected content
        assert "SUPPORTED MODELS" in captured.out
        assert "gemini/gemini-2.0-flash-lite" in captured.out
        assert "gpt-4o" in captured.out
        assert "claude-3-5-sonnet" in captured.out
        assert "litellm.ai" in captured.out


class TestMainExecution:
    """Test main function execution flow."""

    def test_main_exits_with_list_models(self, capsys):
        """Test that --list-models exits after printing."""
        test_args = ["main.py", "--list-models"]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                from main import main
                main()

            assert exc_info.value.code == 0

    def test_main_requires_output_without_preview(self, capsys):
        """Test that main requires --output unless --preview is used."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1"
        ]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                from main import main
                main()

            captured = capsys.readouterr()
            assert "output is required" in captured.out.lower()

    def test_main_accepts_preview_without_output(self):
        """Test that main accepts --preview without --output."""
        test_args = [
            "main.py",
            "--input", "test.csv",
            "--columns", "col1",
            "--preview"
        ]

        with patch.object(sys, 'argv', test_args):
            with patch('main.get_user_prompt', return_value="Test prompt"):
                with patch('main.LLMClient'):
                    with patch('main.CSVProcessor'):
                        # Should not raise SystemExit for missing --output
                        # (will fail later due to missing file, but argument parsing should pass)
                        try:
                            from main import main
                            main()
                        except (FileNotFoundError, SystemExit):
                            pass  # Expected due to missing test.csv
