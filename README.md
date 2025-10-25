# LLM Analyser

A Python tool for processing CSV data using Large Language Models (LLMs) to generate structured output. The tool processes CSV files row-by-row, sends selected columns to an LLM with a custom prompt, and appends the generated structured data as new columns.

Built with [LiteLLM](https://docs.litellm.ai/) for seamless multi-provider support across Gemini, OpenAI, Anthropic, and more.

## Features

- **Multi-Provider LLM Support**: Use Gemini, OpenAI (GPT), Anthropic (Claude), and 100+ other LLMs via LiteLLM
- **Structured JSON Output**: Enforced JSON mode ensures reliable, parseable responses
- **Interactive Prompts**: Specify analysis tasks interactively when running the program
- **Flexible Column Selection**: Choose any combination of columns to pass to the LLM
- **Robust Error Handling**: Automatic retry logic with exponential backoff for API errors
- **Rate Limiting**: Built-in delays to respect API rate limits
- **Sequential Processing**: Process rows one-by-one to avoid overwhelming the API
- **Preview Mode**: Test your prompt on sample rows before processing the entire dataset
- **Easy Provider Switching**: Change LLM providers by simply changing the model name

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- API key for your chosen LLM provider:
  - **Gemini**: [Get API key](https://aistudio.google.com/apikey)
  - **OpenAI**: [Get API key](https://platform.openai.com/api-keys)
  - **Anthropic**: [Get API key](https://console.anthropic.com/)

## Installation

1. Clone or download this repository:

```bash
cd llm-analyser
```

2. Install dependencies using uv:

```bash
uv sync
```

3. Set up your API key:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key(s)
# For Gemini:
# GEMINI_API_KEY=your-gemini-api-key-here
# For OpenAI:
# OPENAI_API_KEY=your-openai-api-key-here
# For Anthropic:
# ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Alternatively, export the API key directly:

```bash
# For Gemini
export GEMINI_API_KEY='your-gemini-api-key-here'

# For OpenAI
export OPENAI_API_KEY='your-openai-api-key-here'

# For Anthropic
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'
```

## Usage

### Basic Usage

```bash
uv run python main.py --input data/yourfile.csv --columns column1,column2 --output results.csv
```

The program will:
1. Prompt you to enter a task description interactively
2. Process each row of the CSV file
3. Send the selected columns to the LLM with your prompt
4. Append the structured output as new columns
5. Save the results to the output file

### Preview Mode

Test your prompt on a few sample rows before processing the entire dataset:

```bash
uv run python main.py --input data/yourfile.csv --columns title,abstract --preview
```

Preview a different number of rows:

```bash
uv run python main.py --input data/yourfile.csv --columns title,abstract --preview --preview-rows 5
```

### Examples

#### Example 1: Sentiment Analysis

```bash
uv run python main.py --input data/reviews.csv --columns review_text --output sentiment_results.csv
```

When prompted, enter:
```
Analyze the sentiment and classify as positive, negative, or neutral. Also provide a confidence score.
```

#### Example 2: Academic Paper Analysis

```bash
uv run python main.py --input data/hsa-miR-144-3p.csv --columns title,abstract --output analysis.csv
```

When prompted, enter:
```
Extract the following information: research_topic, methodology, key_findings, and clinical_significance
```

#### Example 3: Using Different LLM Providers

```bash
# Use Gemini 2.0 Flash Lite (default)
uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv

# Use OpenAI GPT-4o
uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv --model gpt-4o

# Use Anthropic Claude 3.5 Sonnet
uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv --model claude-3-5-sonnet-20241022

# Use OpenAI GPT-4o Mini (cost-effective)
uv run python main.py --input data/papers.csv --columns title,abstract --output results.csv --model gpt-4o-mini
```

#### Example 4: List Available Models

```bash
uv run python main.py --list-models
```

### Command-Line Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--input` | `-i` | Path to input CSV file | Yes |
| `--columns` | `-c` | Comma-separated list of columns to use as LLM input | Yes |
| `--output` | `-o` | Path to output CSV file | Yes (unless `--preview`) |
| `--model` | `-m` | LLM model name (default: `gemini/gemini-2.0-flash-lite`) | No |
| `--list-models` | | List supported models and exit | No |
| `--preview` | `-p` | Preview results on sample rows without saving | No |
| `--preview-rows` | | Number of rows to preview (default: 3) | No |
| `--column-prefix` | | Prefix for new columns (default: `llm_output`) | No |

## How It Works

1. **Input**: The tool reads a CSV file and extracts specified columns
2. **Processing**: For each row:
   - Selected column data is formatted as JSON
   - Combined with your prompt and sent to the LLM
   - LLM generates structured JSON output
   - Retry logic handles API errors automatically
3. **Output**: Generated data is added as new columns with a configurable prefix
4. **Error Handling**:
   - Automatic retries for rate limits (HTTP 429) and transient errors (500, 502, 503, 504)
   - Exponential backoff with configurable wait times
   - Graceful error logging for rows that fail after retries

## Supported Models

LLM Analyser supports 100+ models via LiteLLM. Common examples:

**Gemini Models:**
- `gemini/gemini-2.0-flash-lite` - Fast and lightweight (default)
- `gemini/gemini-1.5-pro` - High quality
- `gemini/gemini-1.5-flash` - Balanced

**OpenAI Models:**
- `gpt-4o` - Latest GPT-4o
- `gpt-4o-mini` - Cost-effective
- `gpt-3.5-turbo` - Fast

**Anthropic Models:**
- `claude-3-5-sonnet-20241022` - High quality
- `claude-3-haiku-20240307` - Fast

For the full list, run `uv run python main.py --list-models` or visit [LiteLLM Providers](https://docs.litellm.ai/docs/providers).

## Configuration

Key configuration options can be found in `llm_analyser/config.py`:

- `DEFAULT_MODEL`: Default model (gemini/gemini-2.0-flash-lite)
- `USE_JSON_MODE`: Force JSON output via LiteLLM (True)
- `MAX_RETRIES`: Maximum number of retry attempts (5)
- `RETRY_MIN_WAIT`: Minimum wait time between retries (1 second)
- `RETRY_MAX_WAIT`: Maximum wait time between retries (60 seconds)
- `REQUEST_DELAY`: Delay between API requests (0.5 seconds)

## Project Structure

```
llm-analyser/
├── main.py                 # CLI entry point
├── llm_analyser/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration settings
│   ├── llm_client.py      # Gemini API client with retry logic
│   └── processor.py       # CSV processing logic
├── data/                   # Input CSV files
├── pyproject.toml         # Project dependencies
├── .env.example           # Example environment variables
└── README.md              # This file
```

## Error Handling

The tool includes comprehensive error handling:

- **API Rate Limits**: Automatic retry with exponential backoff
- **Transient Errors**: Retries for temporary server issues
- **Invalid JSON**: Clear error messages when LLM output isn't valid JSON
- **Missing Columns**: Validation before processing starts
- **Keyboard Interrupt**: Graceful shutdown on Ctrl+C

## Limitations

- **Sequential Processing**: Rows are processed one at a time to respect API rate limits
- **API Costs**: Each row requires an API call, which may incur costs (varies by provider)
- **Model Constraints**: Output quality depends on the LLM model's capabilities
- **JSON Mode**: Some providers may not support JSON mode (will fall back to prompt-based JSON)

## Troubleshooting

### API Key Error

```
Error: API key for gemini not found. Please set the GEMINI_API_KEY environment variable.
```

**Solution**: Make sure you've set the appropriate API key for your chosen model in `.env` or as an environment variable.

### Rate Limit Errors

```
litellm.RateLimitError: 429 Rate limit exceeded
```

**Solution**: The tool will automatically retry with exponential backoff. If errors persist, consider:
- Increasing `REQUEST_DELAY` in `config.py`
- Using a different model with higher rate limits
- Upgrading your API plan

### Invalid JSON Response

```
ValueError: Failed to parse LLM response as JSON
```

**Solution**: Make your prompt more specific about requiring JSON output, or try rephrasing the task.

## Development

### Running Tests

Install development dependencies:

```bash
uv sync --extra dev
```

Run all tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=llm_analyser --cov-report=html
```

Run specific test file:

```bash
uv run pytest tests/test_config.py
```

Run tests by marker:

```bash
uv run pytest -m unit
```

### Test Structure

```
tests/
├── test_config.py       # Configuration tests
├── test_llm_client.py   # LLM client tests (mocked)
├── test_processor.py    # CSV processor tests
├── test_main.py         # CLI tests
└── fixtures/            # Test data
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- Built with [LiteLLM](https://docs.litellm.ai/) for multi-provider LLM support
- Supports [Google Gemini](https://ai.google.dev/), [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), and 100+ LLM providers
- Uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management
- Powered by [pandas](https://pandas.pydata.org/) for CSV processing
