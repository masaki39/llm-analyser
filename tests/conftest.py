"""Pytest configuration and fixtures."""

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return pd.DataFrame(
        {
            "title": [
                "Study of miRNA in cancer",
                "Gene expression analysis",
                "Protein interaction networks",
            ],
            "abstract": [
                "This study investigates the role of microRNA in cancer progression.",
                "We analyzed gene expression patterns across multiple tissues.",
                "Network analysis revealed key protein interactions.",
            ],
            "year": [2023, 2024, 2023],
        }
    )


@pytest.fixture
def sample_csv_file(tmp_path, sample_csv_data):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / "test_data.csv"
    sample_csv_data.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_llm_response():
    """Sample LLM response in JSON format."""
    return {
        "category": "medical_research",
        "sentiment": "neutral",
        "key_topics": ["miRNA", "cancer", "biomarker"],
    }


@pytest.fixture
def sample_llm_response_with_markdown():
    """Sample LLM response wrapped in markdown code block."""
    return """```json
{
    "category": "medical_research",
    "sentiment": "neutral",
    "key_topics": ["miRNA", "cancer", "biomarker"]
}
```"""


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"
