"""LLM client with retry logic using LiteLLM for multi-provider support."""

import json
import logging
import os
import time
from typing import Any, Dict, Optional, Type

import litellm
from litellm import completion, supports_response_schema
from litellm.exceptions import (
    APIError,
    RateLimitError,
    ServiceUnavailableError,
    Timeout,
)
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import (
    API_KEY_ENV_VARS,
    DEFAULT_MODEL,
    MAX_RETRIES,
    REQUEST_DELAY,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
    RETRY_MULTIPLIER,
    USE_JSON_MODE,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with multiple LLM providers via LiteLLM with retry logic."""

    def __init__(self, model_name: str = DEFAULT_MODEL, api_key: str | None = None):
        """Initialize the LLM client.

        Args:
            model_name: Name of the model to use (e.g., "gemini/gemini-2.5-flash-lite", "gpt-4o").
            api_key: Optional API key. If None, LiteLLM will use standard environment variables.

        Raises:
            ValueError: If required API key is not found in environment.
        """
        self.model_name = model_name
        self.last_request_time = 0

        # Determine provider from model name
        self.provider = self._detect_provider(model_name)

        # Set up API key if provided
        if api_key:
            self._set_api_key(api_key)
        else:
            # Verify that appropriate env var is set
            self._verify_api_key()

        # Configure LiteLLM
        litellm.drop_params = True  # Drop unsupported params instead of erroring
        litellm.set_verbose = False  # Disable verbose logging
        litellm.enable_json_schema_validation = True  # Enable client-side validation

        # Check if model supports response schema
        self.supports_schema = supports_response_schema(model_name)

    def _detect_provider(self, model_name: str) -> str:
        """Detect the provider from the model name.

        Args:
            model_name: The model name.

        Returns:
            The provider name (e.g., "gemini", "openai", "anthropic").
        """
        if model_name.startswith("gemini/"):
            return "gemini"
        elif model_name.startswith("gpt-") or model_name.startswith("openai/"):
            return "openai"
        elif model_name.startswith("claude-") or model_name.startswith("anthropic/"):
            return "anthropic"
        else:
            # Default to checking if it's a known prefix
            for provider in API_KEY_ENV_VARS.keys():
                if model_name.startswith(f"{provider}/"):
                    return provider
            return "unknown"

    def _set_api_key(self, api_key: str) -> None:
        """Set the API key for the detected provider.

        Args:
            api_key: The API key to set.
        """
        env_var = API_KEY_ENV_VARS.get(self.provider)
        if env_var:
            os.environ[env_var] = api_key

    def _verify_api_key(self) -> None:
        """Verify that the required API key is set in environment.

        Raises:
            ValueError: If the required API key is not found.
        """
        env_var = API_KEY_ENV_VARS.get(self.provider)
        if not env_var:
            # Unknown provider, log warning
            logger.warning(
                f"Unknown provider '{self.provider}' for model '{self.model_name}'. "
                f"API key verification skipped. Ensure appropriate environment variables are set."
            )
            return

        if not os.getenv(env_var):
            raise ValueError(
                f"API key for {self.provider} not found. "
                f"Please set the {env_var} environment variable.\n"
                f"Example: export {env_var}='your-api-key-here'"
            )

    def _rate_limit_delay(self) -> None:
        """Implement rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    @retry(
        retry=retry_if_exception_type(
            (
                RateLimitError,
                ServiceUnavailableError,
                APIError,
                Timeout,
            )
        ),
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(
            multiplier=RETRY_MULTIPLIER,
            min=RETRY_MIN_WAIT,
            max=RETRY_MAX_WAIT,
        ),
        reraise=True,
    )
    def _generate_with_retry(
        self, messages: list, response_model: Optional[Type[BaseModel]] = None
    ) -> str:
        """Generate content with automatic retry logic.

        Args:
            messages: List of message dictionaries for the chat completion.
            response_model: Optional Pydantic model for structured output.

        Returns:
            The generated text response.

        Raises:
            Various LiteLLM exceptions if retries are exhausted.
        """
        self._rate_limit_delay()

        # Build completion parameters
        completion_params = {
            "model": self.model_name,
            "messages": messages,
        }

        # Add response format based on whether we have a schema
        if response_model is not None:
            if self.supports_schema:
                # Use Pydantic model directly (LiteLLM will handle conversion)
                completion_params["response_format"] = response_model
            else:
                # Fallback to json_object mode
                completion_params["response_format"] = {"type": "json_object"}
        elif USE_JSON_MODE:
            completion_params["response_format"] = {"type": "json_object"}

        response = completion(**completion_params)
        return response.choices[0].message.content

    def generate_structured_output(
        self,
        prompt: str,
        input_data: Dict[str, Any],
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """Generate structured output from input data.

        Args:
            prompt: The user-provided prompt describing the task.
            input_data: Dictionary containing the selected column data.
            response_model: Optional Pydantic model defining the output schema.

        Returns:
            Dictionary containing the generated structured output.

        Raises:
            ValueError: If the response cannot be parsed as JSON or validated.
        """
        # Construct the messages for chat completion
        data_str = json.dumps(input_data, ensure_ascii=False, indent=2)

        # Build system message based on whether we have a schema
        if response_model is not None:
            schema_fields = list(response_model.model_fields.keys())
            system_message = (
                "You are a data analyst. You must respond ONLY with valid JSON matching the required schema. "
                f"Required fields: {', '.join(schema_fields)}. "
                "Do not include any markdown formatting, explanations, or text outside the JSON object."
            )
        else:
            system_message = (
                "You are a data analyst. You must respond ONLY with valid JSON. "
                "Do not include any markdown formatting, explanations, or text outside the JSON object."
            )

        user_message = f"""Based on the following data and task description, generate a structured output in valid JSON format.

Task: {prompt}

Input Data:
{data_str}

Instructions:
- Analyze the input data according to the task description
- Return ONLY a valid JSON object with your analysis results
- The JSON should contain relevant fields based on the task
- Do not include any explanation or markdown formatting

Output (JSON only):"""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        try:
            response_text = self._generate_with_retry(messages, response_model)

            # Clean up response text (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse JSON response
            result = json.loads(response_text)

            if not isinstance(result, dict):
                raise ValueError("Response must be a JSON object (dictionary)")

            # Validate against Pydantic model if provided
            if response_model is not None:
                try:
                    validated = response_model(**result)
                    # Convert back to dict for consistency
                    return validated.model_dump()
                except Exception as e:
                    raise ValueError(
                        f"Response does not match expected schema: {e}"
                    ) from e

            return result

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse LLM response as JSON: {e}\n"
                f"Response was: {response_text[:200]}..."
            ) from e
        except Exception as e:
            raise ValueError(f"Error generating structured output: {e}") from e
