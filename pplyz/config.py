"""Configuration settings for LLM Analyser."""

import os
from pathlib import Path

# API Configuration
DEFAULT_MODEL_ENV_VAR = "PPLYZ_DEFAULT_MODEL"
DEFAULT_MODEL_FALLBACK = "gemini/gemini-2.5-flash-lite"


def get_default_model() -> str:
    """Return the default model, allowing override via environment variable."""
    return os.getenv(DEFAULT_MODEL_ENV_VAR, DEFAULT_MODEL_FALLBACK)


DEFAULT_MODEL = get_default_model()

# Multi-provider API key environment variables (per LiteLLM docs)
# Each provider entry lists accepted env var names in priority order.
API_KEY_ENV_VARS = {
    "gemini": ["GEMINI_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "claude": ["ANTHROPIC_API_KEY"],
    "groq": ["GROQ_API_KEY"],
    "mistral": ["MISTRAL_API_KEY"],
    "mistralai": ["MISTRAL_API_KEY"],
    "cohere": ["COHERE_API_KEY"],
    "replicate": ["REPLICATE_API_KEY"],
    "huggingface": ["HUGGINGFACE_API_KEY"],
    "together_ai": ["TOGETHERAI_API_KEY", "TOGETHER_AI_TOKEN"],
    "perplexity": ["PERPLEXITY_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "xai": ["XAI_API_KEY"],
    "openrouter": ["OPENROUTER_API_KEY"],
    "azure": ["AZURE_OPENAI_API_KEY", "AZURE_API_KEY"],
    "bedrock": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
    "sagemaker": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
    "vertex_ai": ["GOOGLE_APPLICATION_CREDENTIALS"],
    "vertex_ai_beta": ["GOOGLE_APPLICATION_CREDENTIALS"],
    "watsonx": ["WATSONX_API_KEY", "WATSONX_APIKEY"],
    "databricks": ["DATABRICKS_TOKEN", "DATABRICKS_KEY"],
    "cohere_chat": ["COHERE_API_KEY"],
    "fireworks_ai": ["FIREWORKS_API_KEY", "FIREWORKSAI_API_KEY"],
    "cloudflare": ["CLOUDFLARE_API_KEY"],
}

# Supported models (examples - LiteLLM supports many more)
SUPPORTED_MODELS = {
    # Gemini (Google)
    "gemini/gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite (default, cost-effective)",
    "gemini/gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite (fast)",
    "gemini/gemini-1.5-pro": "Gemini 1.5 Pro (high quality)",
    # OpenAI
    "gpt-4o": "GPT-4o (flagship)",
    "gpt-4o-mini": "GPT-4o Mini (fast + cheap)",
    # Anthropic
    "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (balanced)",
    "claude-3-haiku-20240307": "Claude 3 Haiku (fast)",
    # Groq
    "groq/llama-3.1-8b-instant": "Groq Llama 3.1 8B Instant (ultra-low latency)",
    # Mistral
    "mistral/mistral-large-latest": "Mistral Large Latest (enterprise-ready)",
    # Cohere
    "cohere/command-r-plus": "Cohere Command R+ (tool + reasoning)",
    # Together AI
    "together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": "Together Meta-Llama 3.1 70B (API aggregators)",
    # Replicate
    "replicate/meta/meta-llama-3-8b-instruct": "Replicate Meta Llama 3 8B Instruct",
    # Hugging Face Inference Endpoints
    "huggingface/meta-llama/Meta-Llama-3-8B-Instruct": "Hugging Face Inference: Meta-Llama-3-8B-Instruct",
    # xAI
    "xai/grok-beta": "xAI Grok Beta",
    # Amazon Bedrock
    "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0": "Amazon Bedrock Claude 3.5 Haiku",
    # Google Vertex AI
    "vertex_ai/gemini-1.5-pro-preview-0409": "Vertex AI Gemini 1.5 Pro Preview",
    # IBM watsonx
    "watsonx/granite-3-8b-instruct": "IBM watsonx Granite 3 8B Instruct",
    # Perplexity
    "perplexity/llama-3.1-sonar-small-128k-online": "Perplexity Sonar Small (web-augmented)",
    # DeepSeek
    "deepseek/deepseek-chat": "DeepSeek Chat",
    # OpenRouter
    "openrouter/meta-llama/Meta-Llama-3-70B-Instruct": "OpenRouter Meta-Llama 3 70B Instruct",
    # Azure OpenAI
    "azure/gpt-4o": "Azure OpenAI GPT-4o (enterprise)",
    # Databricks
    "databricks/mixtral-8x7b-instruct": "Databricks Mixtral 8x7B Instruct",
    # AWS SageMaker
    "sagemaker/meta-textgeneration-llama-3-8b": "SageMaker Llama 3 8B Text Generation",
}

# Retry Configuration
RETRY_BACKOFF_SCHEDULE = [1, 2, 3, 5, 10, 10, 10, 10, 10]  # seconds
MAX_RETRIES = len(RETRY_BACKOFF_SCHEDULE) + 1  # initial attempt + retries

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
