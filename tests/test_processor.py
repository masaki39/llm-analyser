"""Tests for CSV processor module."""

from unittest.mock import patch

import pandas as pd
import pytest

from llman.processor import CSVProcessor


class TestCSVProcessorInit:
    """Test CSV processor initialization."""

    def test_init_with_llm_client(self, mock_env_vars):
        """Test processor initialization with LLM client."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        assert processor.llm_client == client


class TestProcessCSV:
    """Test CSV processing functionality."""

    def test_process_csv_with_valid_input(
        self, sample_csv_file, tmp_path, mock_env_vars
    ):
        """Test processing CSV with valid input."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        output_path = tmp_path / "output.csv"

        # Mock the LLM client's generate_structured_output
        with patch.object(client, "generate_structured_output") as mock_generate:
            mock_generate.return_value = {"category": "test", "score": 0.9}

            processor.process_csv(
                input_path=sample_csv_file,
                output_path=output_path,
                columns=["title", "abstract"],
                prompt="Classify this research",
            )

            # Check output file exists
            assert output_path.exists()

            # Check output has new columns
            output_df = pd.read_csv(output_path)
            assert "category" in output_df.columns
            assert "score" in output_df.columns

    def test_process_csv_with_missing_file(self, tmp_path, mock_env_vars):
        """Test processing non-existent CSV file raises error."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        with pytest.raises(FileNotFoundError):
            processor.process_csv(
                input_path=tmp_path / "nonexistent.csv",
                output_path=tmp_path / "output.csv",
                columns=["title"],
                prompt="Test",
            )

    def test_process_csv_with_invalid_columns(
        self, sample_csv_file, tmp_path, mock_env_vars
    ):
        """Test processing CSV with invalid column names raises error."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        with pytest.raises(ValueError, match="Columns not found"):
            processor.process_csv(
                input_path=sample_csv_file,
                output_path=tmp_path / "output.csv",
                columns=["nonexistent_column"],
                prompt="Test",
            )

    def test_process_csv_handles_row_errors(
        self, sample_csv_file, tmp_path, mock_env_vars
    ):
        """Test that processor continues when individual rows fail."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        output_path = tmp_path / "output.csv"

        with patch.object(client, "generate_structured_output") as mock_generate:
            # First row succeeds, second fails, third succeeds
            mock_generate.side_effect = [
                {"status": "success"},
                ValueError("Test error"),
                {"status": "success"},
            ]

            processor.process_csv(
                input_path=sample_csv_file,
                output_path=output_path,
                columns=["title"],
                prompt="Test",
            )

            # Output file should still be created
            assert output_path.exists()

            # Should have processed all rows (with empty dict for failed row)
            output_df = pd.read_csv(output_path)
            assert len(output_df) == 3


class TestPreviewSample:
    """Test preview sample functionality."""

    def test_preview_sample_with_valid_input(
        self, sample_csv_file, mock_env_vars, capsys
    ):
        """Test preview mode with valid input."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        with patch.object(client, "generate_structured_output") as mock_generate:
            mock_generate.return_value = {"preview": "result"}

            processor.preview_sample(
                input_path=sample_csv_file,
                columns=["title", "abstract"],
                prompt="Test preview",
                num_rows=2,
            )

            # Check that generate was called twice (for 2 rows)
            assert mock_generate.call_count == 2

    def test_preview_sample_with_missing_columns(self, sample_csv_file, mock_env_vars):
        """Test preview with invalid columns raises error."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        with pytest.raises(ValueError, match="Columns not found"):
            processor.preview_sample(
                input_path=sample_csv_file,
                columns=["invalid_column"],
                prompt="Test",
            )

    def test_preview_sample_default_num_rows(self, sample_csv_file, mock_env_vars):
        """Test preview uses default 3 rows."""
        from llman.llm_client import LLMClient

        client = LLMClient(model_name="gemini/gemini-2.5-flash-lite")
        processor = CSVProcessor(llm_client=client)

        with patch.object(client, "generate_structured_output") as mock_generate:
            mock_generate.return_value = {"preview": "result"}

            processor.preview_sample(
                input_path=sample_csv_file, columns=["title"], prompt="Test"
            )

            # Default is 3 rows, but sample CSV only has 3 rows
            assert mock_generate.call_count == 3
