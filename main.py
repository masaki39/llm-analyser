#!/usr/bin/env python3
"""LLM Analyser - CSV data processing with LLM-powered structured output generation."""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from llman.config import (
    API_KEY_ENV_VARS,
    DATA_DIR,
    SUPPORTED_MODELS,
    get_default_model,
)
from llman.llm_client import LLMClient
from llman.processor import CSVProcessor
from llman.schemas import create_output_model_from_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Simple format for user-facing output
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Process CSV files with LLM to generate structured data columns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a CSV file with interactive prompt
  uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv

  # Preview results on sample rows before full processing
  uv run python main.py --input data/papers.csv --columns title,abstract --preview

  # Use a custom model
  uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv --model gemini-2.5-flash-lite

Environment Variables:
  GEMINI_API_KEY      Gemini API key (for Gemini models)
  OPENAI_API_KEY      OpenAI API key (for GPT models)
  ANTHROPIC_API_KEY   Anthropic API key (for Claude models)
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        type=str,
        help="Path to input CSV file",
    )

    parser.add_argument(
        "--columns",
        "-c",
        type=str,
        help="Comma-separated list of columns to use as LLM input (e.g., 'title,abstract,keywords')",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to output CSV file (optional, defaults to input file)",
    )

    default_model = get_default_model()

    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default=default_model,
        help=f"LLM model name (default: {default_model}). Supports Gemini, OpenAI, Anthropic models via LiteLLM.",
    )

    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        dest="list_models",
        help="List supported models and exit",
    )

    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Preview results on sample rows without saving (3 rows by default)",
    )

    parser.add_argument(
        "--preview-rows",
        type=int,
        default=3,
        help="Number of rows to preview when using --preview (default: 3)",
    )

    field_help = (
        'Output fields definition (e.g., "is_relevant:bool,summary:str,keywords:list[str]"). '
        "Supported types: bool, int, float, str, list[str], list[int], list[float], "
        "list[bool], dict. Omitting :type defaults to str."
    )

    parser.add_argument(
        "--fields",
        "-f",
        type=str,
        help=field_help,
    )

    parser.add_argument(
        "--no-resume",
        "-R",
        action="store_true",
        help="Disable resume mode (always process all rows, even if output exists)",
    )

    return parser.parse_args()


def get_user_prompt() -> str:
    """Get the analysis prompt from user interactively.

    Returns:
        The user-provided prompt.
    """
    print("\n" + "=" * 60)
    print("LLM ANALYSER - Interactive Prompt Input")
    print("=" * 60)
    print(
        "\nPlease describe the task you want the LLM to perform on each row.\n"
        "The LLM will receive the selected columns and generate structured output.\n"
    )
    print("Examples:")
    print('  - "Classify the sentiment as positive, negative, or neutral"')
    print('  - "Extract key findings and methodology from the abstract"')
    print('  - "Summarize the main topic in 1-2 sentences"\n')

    prompt = input("Enter your task description: ").strip()

    if not prompt:
        print("Error: Prompt cannot be empty")
        sys.exit(1)

    return prompt


def list_supported_models() -> None:
    """Print list of supported models."""
    print("\n" + "=" * 70)
    print("SUPPORTED MODELS")
    print("=" * 70)
    print("\nNote: LiteLLM supports many more models. These are common examples.\n")

    for model_name, description in SUPPORTED_MODELS.items():
        print(f"  {model_name}")
        print(f"    {description}\n")

    print("=" * 70)
    print("\nFor the full list, visit: https://docs.litellm.ai/docs/providers")
    print()


def main() -> None:
    """Main entry point for the LLM Analyser CLI."""
    # Load environment variables from .env file if present
    load_dotenv()

    # Parse arguments
    args = parse_arguments()

    # Handle --list
    if args.list_models:
        list_supported_models()
        sys.exit(0)

    # Validate required arguments (only if not using --list)
    if not args.input or not args.columns:
        print("Error: the following arguments are required: --input/-i, --columns/-c")
        print("Use --help for more information")
        sys.exit(1)

    # Parse columns
    columns = [col.strip() for col in args.columns.split(",")]

    if not columns:
        print("Error: At least one column must be specified")
        sys.exit(1)

    # Resolve input path
    input_path = Path(args.input)
    if not input_path.is_absolute():
        # Try relative to DATA_DIR first
        data_path = DATA_DIR / input_path
        if data_path.exists():
            input_path = data_path
        else:
            # Use as relative to current directory
            input_path = input_path.resolve()

    # Get user prompt interactively
    prompt = get_user_prompt()

    # Create response model from schema/fields if provided
    response_model = None
    if args.fields:
        try:
            response_model = create_output_model_from_string(args.fields)
            print(f"\n✓ Using fields: {args.fields}")
        except Exception as e:
            print(f"Error parsing fields: {e}")
            sys.exit(1)

    # Initialize LLM client
    logger.info(f"\nInitializing LLM client (model: {args.model})...")
    try:
        llm_client = LLMClient(model_name=args.model)
        logger.info(f"✓ LLM client initialized (provider: {llm_client.provider})")
    except ValueError as e:
        logger.error(f"Error: {e}")
        logger.error("\nPlease set the appropriate API key for your chosen model.")
        logger.error("For example:")
        for provider, env_var in API_KEY_ENV_VARS.items():
            logger.error(
                f"  export {env_var}='your-api-key-here'  # For {provider} models"
            )
        logger.error("\nOr create a .env file with the appropriate API key.")
        sys.exit(1)

    # Initialize processor
    processor = CSVProcessor(llm_client)

    try:
        if args.preview:
            # Preview mode
            processor.preview_sample(
                input_path=input_path,
                columns=columns,
                prompt=prompt,
                num_rows=args.preview_rows,
                response_model=response_model,
            )
        else:
            # Full processing mode
            # Default output to input if not specified
            output_path = Path(args.output) if args.output else input_path
            processor.process_csv(
                input_path=input_path,
                output_path=output_path,
                columns=columns,
                prompt=prompt,
                response_model=response_model,
                resume=not args.no_resume,
            )

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
