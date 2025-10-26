"""Tests for configuration module."""

from llm_analyser import config


class TestConfig:
    """Test configuration values."""

    def test_default_model(self):
        """Test default model is set correctly."""
        assert config.DEFAULT_MODEL == "gemini/gemini-2.5-flash-lite"

    def test_api_key_env_vars(self):
        """Test API key environment variable mappings."""
        assert "gemini" in config.API_KEY_ENV_VARS
        assert "openai" in config.API_KEY_ENV_VARS
        assert "anthropic" in config.API_KEY_ENV_VARS

        assert config.API_KEY_ENV_VARS["gemini"] == "GEMINI_API_KEY"
        assert config.API_KEY_ENV_VARS["openai"] == "OPENAI_API_KEY"
        assert config.API_KEY_ENV_VARS["anthropic"] == "ANTHROPIC_API_KEY"

    def test_supported_models(self):
        """Test supported models dictionary."""
        assert isinstance(config.SUPPORTED_MODELS, dict)
        assert len(config.SUPPORTED_MODELS) > 0

        # Check some key models exist
        assert "gemini/gemini-2.5-flash-lite" in config.SUPPORTED_MODELS
        assert "gemini/gemini-2.0-flash-lite" in config.SUPPORTED_MODELS
        assert "gpt-4o" in config.SUPPORTED_MODELS
        assert "claude-3-5-sonnet-20241022" in config.SUPPORTED_MODELS

    def test_retry_config(self):
        """Test retry configuration values."""
        assert config.MAX_RETRIES == 5
        assert config.RETRY_MIN_WAIT == 1
        assert config.RETRY_MAX_WAIT == 60
        assert config.RETRY_MULTIPLIER == 2

    def test_rate_limit_codes(self):
        """Test rate limit HTTP codes."""
        assert 429 in config.RATE_LIMIT_CODES

    def test_transient_error_codes(self):
        """Test transient error HTTP codes."""
        assert 500 in config.TRANSIENT_ERROR_CODES
        assert 502 in config.TRANSIENT_ERROR_CODES
        assert 503 in config.TRANSIENT_ERROR_CODES
        assert 504 in config.TRANSIENT_ERROR_CODES

    def test_processing_config(self):
        """Test processing configuration."""
        assert config.DEFAULT_BATCH_SIZE == 1
        assert config.REQUEST_DELAY == 0.5

    def test_json_mode_enabled(self):
        """Test JSON mode is enabled."""
        assert config.USE_JSON_MODE is True

    def test_project_paths(self):
        """Test project paths are set."""
        assert config.PROJECT_ROOT.exists()
        assert config.DATA_DIR.exists()
