"""Configuration settings for LLM Analyser."""

import os
from pathlib import Path

# API Configuration
DEFAULT_MODEL = "gemini/gemini-2.5-flash-lite"

# Multi-provider API key environment variables
# LiteLLM automatically uses standard env vars for each provider
API_KEY_ENV_VARS = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
}

# Supported models (examples - LiteLLM supports many more)
SUPPORTED_MODELS = {
    # Gemini models
    "gemini/gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (fast, lightweight, default)",
    "gemini/gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite (fast, lightweight)",
    "gemini/gemini-1.5-pro": "Gemini 1.5 Pro (high quality)",
    "gemini/gemini-1.5-flash": "Gemini 1.5 Flash (balanced)",
    # OpenAI models
    "gpt-4o": "GPT-4o (latest)",
    "gpt-4o-mini": "GPT-4o Mini (cost-effective)",
    "gpt-3.5-turbo": "GPT-3.5 Turbo (fast)",
    # Anthropic models
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (high quality)",
    "claude-3-haiku-20240307": "Claude 3 Haiku (fast)",
}

# Retry Configuration
MAX_RETRIES = 5
RETRY_MIN_WAIT = 1  # seconds
RETRY_MAX_WAIT = 60  # seconds
RETRY_MULTIPLIER = 2  # exponential backoff multiplier

# Rate Limiting
RATE_LIMIT_CODES = [429]  # HTTP status codes that trigger rate limit retry
TRANSIENT_ERROR_CODES = [500, 502, 503, 504]  # Transient errors to retry

# Processing Configuration
DEFAULT_BATCH_SIZE = 1  # Process one row at a time to respect API limits
REQUEST_DELAY = 0.5  # seconds between requests to avoid rate limiting

# JSON Mode Configuration
USE_JSON_MODE = True  # Force JSON output via LiteLLM

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
