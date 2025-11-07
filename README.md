# LLM Analyser (llman)

**llman** is a Python tool for processing CSV data using Large Language Models (LLMs) to generate structured output. The name "llman" is short for "LLM Analyser". The tool processes CSV files row-by-row, sends selected columns to an LLM with a custom prompt, and appends the generated structured data as new columns.

Built with [LiteLLM](https://docs.litellm.ai/) for seamless multi-provider support across Gemini, OpenAI, Anthropic, and more.

## Features

- **Multi-Provider LLM Support**: Use Gemini, OpenAI (GPT), Anthropic (Claude), and 100+ other LLMs via LiteLLM
- **Structured JSON Output**: Enforced JSON mode ensures reliable, parseable responses
- **Interactive Prompts**: Specify analysis tasks interactively when running the program
- **Flexible Column Selection**: Choose any combination of columns to pass to the LLM
- **Robust Error Handling**: Automatic retry logic with exponential backoff for API errors
- **Automatic Recovery**: Failed rows are retried once more before writing the CSV, reducing blank outputs
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
cd llman
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
# Override default model (optional):
# LLMAN_DEFAULT_MODEL=gemini/gemini-2.5-flash-lite
# For Groq / Mistral / Cohere / etc. see the table below
```

Alternatively, export the API key directly:

```bash
# For Gemini
export GEMINI_API_KEY='your-gemini-api-key-here'

# For OpenAI
export OPENAI_API_KEY='your-openai-api-key-here'

# For Anthropic
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'
# Override default model (optional)
export LLMAN_DEFAULT_MODEL='groq/llama-3.1-8b-instant'
# For Groq
export GROQ_API_KEY='your-groq-api-key-here'
# For Mistral
export MISTRAL_API_KEY='your-mistral-api-key-here'
# For Cohere
export COHERE_API_KEY='your-cohere-api-key-here'
```

### Common Provider Environment Variables

| Provider | Example Model Prefix | Environment Variables |
|----------|---------------------|------------------------|
| Default model override | *(applies globally)* | `LLMAN_DEFAULT_MODEL` |
| Google Gemini | `gemini/` | `GEMINI_API_KEY` |
| OpenAI | `gpt-` or `openai/` | `OPENAI_API_KEY` |
| Anthropic / Claude | `claude-` or `anthropic/` | `ANTHROPIC_API_KEY` |
| Groq | `groq/` | `GROQ_API_KEY` |
| Mistral AI | `mistral/` | `MISTRAL_API_KEY` |
| Cohere | `cohere/` | `COHERE_API_KEY` |
| Together AI | `together_ai/` | `TOGETHERAI_API_KEY` or `TOGETHER_AI_TOKEN` |
| Replicate | `replicate/` | `REPLICATE_API_KEY` |
| Hugging Face Inference | `huggingface/` | `HUGGINGFACE_API_KEY` |
| xAI (Grok) | `xai/` | `XAI_API_KEY` |
| OpenRouter | `openrouter/` | `OPENROUTER_API_KEY` |
| GroqCloud | `groq/` | `GROQ_API_KEY` |
| DeepSeek | `deepseek/` | `DEEPSEEK_API_KEY` |
| Perplexity | `perplexity/` | `PERPLEXITY_API_KEY` |
| Google Vertex AI | `vertex_ai/` | `GOOGLE_APPLICATION_CREDENTIALS` (path to service account JSON) |
| Azure OpenAI | `azure/` | `AZURE_OPENAI_API_KEY` (plus endpoint/deployment vars) |
| Amazon Bedrock / SageMaker | `bedrock/`, `sagemaker/` | Standard AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) |
| IBM watsonx | `watsonx/` | `WATSONX_API_KEY` or `WATSONX_APIKEY` |
| Databricks | `databricks/` | `DATABRICKS_TOKEN` |

Set any combination of keys in `.env` to toggle providers instantly. Run `uv run python main.py --list` (or `-l`) to see the bundled examples, or supply any LiteLLM-supported model string manually.

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

#### Example 4: Boolean-Based Classification (Recommended)

```bash
uv run python main.py \
  --input data/articles.csv \
  --columns title,abstract \
  --fields 'is_relevant:bool,summary:str' \
  --output classified.csv
```

When prompted, enter:
```
Determine if this article is relevant to climate change research (true/false).
Provide a one-sentence summary.
```

**Why this works well**: Boolean fields guarantee only `true`/`false` values, avoiding ambiguous responses like "yes", "maybe", or "unclear".

#### Example 5: List Available Models

```bash
uv run python main.py --list
```

### Command-Line Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--input` | `-i` | Path to input CSV file | Yes |
| `--columns` | `-c` | Comma-separated list of columns to use as LLM input | Yes |
| `--output` | `-o` | Path to output CSV file | Yes (unless `--preview`) |
| `--model` | `-m` | LLM model name (default: `LLMAN_DEFAULT_MODEL` or `gemini/gemini-2.5-flash-lite`) | No |
| `--list` | `-l` | List supported models and exit | No |
| `--preview` | `-p` | Preview results on sample rows without saving | No |
| `--preview-rows` | | Number of rows to preview (default: 3) | No |
| `--fields` | `-f` | Field definition string (e.g., `"field1:str,field2:int"`) | No |
| `--no-resume` | `-R` | Reprocess all rows even if output exists | No |

## Best Practices for Field Definitions

### Defining Fields

Use `--fields` to describe the JSON structure you expect back:

```bash
--fields "is_relevant:bool,summary:str,keywords:list[str]"
```

Any field without `:type` defaults to `str`. Supported types: `bool`, `int`, `float`, `str`, `list[str]`, `list[int]`, `list[float]`, `list[bool]`, and `dict`.

### Field Design Patterns

#### Pattern 1: Binary Classification (Most Reliable) ✅

Use **boolean fields** for yes/no decisions - these are strictly enforced across all LLM providers:

```bash
uv run python main.py \
  --input data.csv \
  --columns title,abstract \
  --fields "is_relevant:bool,reason:str" \
  --output results.csv
```

**Why boolean?** Unlike string fields, boolean type guarantees only `true` or `false` values - no unexpected strings like "yes", "maybe", or "unknown".

#### Pattern 2: Multi-level Classification (Requires Care) ⚠️

For granular classifications (e.g., high/medium/low), understand the limitations:

```bash
--fields "relevance:str,confidence:str,notes:str"
```

**Important**: String fields don't enforce enum constraints. LLMs may return unexpected values.

**Best Practice**:
1. Use very explicit prompts listing all allowed values
2. Consider post-processing for production use
3. Consider using boolean flags instead (see Pattern 3)

#### Pattern 3: Hybrid Approach (Recommended for Production) 🎯

Combine boolean gates with descriptive fields:

```bash
--fields "is_dish_related:bool,confidence_level:str,explanation:str"
```

Then in your prompt:
```
First, determine if the article is DISH-related (true/false).
Then rate confidence as "high", "medium", or "low".
Provide a brief explanation.
```

**Advantages**:
- Boolean field provides reliable binary classification
- String fields provide additional context
- Works consistently across all providers

### Supported Field Types

| Type | Enforcement Level | Use Case | Example |
|------|------------------|----------|---------|
| `bool` | ✅ Strict (`true`/`false` only) | Binary decisions | `"is_relevant": "bool"` |
| `int` | ✅ Strict (integers only) | Counts, scores | `"score": "int"` |
| `float` | ✅ Strict (numbers only) | Decimal scores | `"confidence": "float"` |
| `str` | ⚠️ Flexible (any text) | Descriptions, reasons | `"summary": "str"` |
| `list[str]` | ⚠️ Flexible (JSON array) | Tags, keywords | `"tags": "list[str]"` |

### Understanding Output Validation Levels

LLM Analyser supports three levels of validation through LiteLLM:

1. **JSON Syntax Only** (basic mode)
   - Ensures valid JSON structure
   - No field or type validation

2. **Type Validation** (with `--fields`)
   - Enforces field presence and types
   - Boolean, int, float strictly enforced
   - Strings accept any text

3. **Enum/Pattern Validation** (limited support)
   - Only supported by some models (e.g., OpenAI GPT-4o)
   - Not universally available
   - **Requires post-processing for most models**

### Provider-Specific Behavior

| Provider | Boolean/Int/Float | String Enums | Recommendation |
|----------|-------------------|--------------|----------------|
| OpenAI (GPT-4o) | ✅ Excellent | ✅ Good | Best for strict schemas |
| Anthropic (Claude) | ✅ Excellent | ⚠️ Moderate | Good JSON, use strong prompts |
| Gemini (Flash) | ✅ Good | ❌ Limited | Boolean + post-processing |
| Others | Varies | ❌ Limited | Test thoroughly |

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
- `gemini/gemini-2.5-flash-lite` - Fast and lightweight (default)
- `gemini/gemini-2.0-flash-lite` - Fast and lightweight
- `gemini/gemini-1.5-pro` - High quality
- `gemini/gemini-1.5-flash` - Balanced

**OpenAI Models:**
- `gpt-4o` - Latest GPT-4o
- `gpt-4o-mini` - Cost-effective
- `gpt-3.5-turbo` - Fast

**Anthropic Models:**
- `claude-3-5-sonnet-20241022` - High quality
- `claude-3-haiku-20240307` - Fast

For the full list, run `uv run python main.py --list` (or `-l`) or visit [LiteLLM Providers](https://docs.litellm.ai/docs/providers).

## Configuration

Key configuration options can be found in `llman/config.py`:

- `DEFAULT_MODEL`: Default model (gemini/gemini-2.5-flash-lite). Override by setting `LLMAN_DEFAULT_MODEL` in `.env`.
- `USE_JSON_MODE`: Force JSON output via LiteLLM (True)
- `MAX_RETRIES`: Maximum number of retry attempts (`len(RETRY_BACKOFF_SCHEDULE) + 1`)
- `RETRY_BACKOFF_SCHEDULE`: Fixed delays between retries (`[1, 2, 3, 5, 10, 10, 10, 10, 10]` seconds)
- `REQUEST_DELAY`: Delay between API requests (0.5 seconds)

## Project Structure

```
llman/
├── main.py                 # CLI entry point
├── llman/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration settings
│   ├── llm_client.py      # LLM API client with retry logic
│   ├── processor.py       # CSV processing logic
│   └── schemas.py         # Output schema definitions
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

### Unexpected Output Values

**Problem**: LLM returns values outside your expected range (e.g., "yes"/"no" instead of "high"/"middle"/"low").

**Why this happens**:
- String fields (`"str"`) only enforce type, not specific values
- LLMs may interpret instructions creatively
- Enum constraints are not universally supported across all providers

**Solutions**:

1. **Use boolean fields for binary decisions** (RECOMMENDED):
   ```bash
   --fields "is_relevant:bool,reason:str"
   ```
   Boolean fields strictly enforce `true`/`false` values across all providers.

2. **Choose models with better instruction-following**:
   - OpenAI GPT-4o: Best enum constraint support
   - Anthropic Claude: Strong instruction-following
   - Gemini Flash: Good for general use

3. **Strengthen your prompt**:
   - Provide explicit examples
   - Use "You MUST output only: X, Y, or Z"
   - Add example output in the prompt

4. **Use preview mode to validate**:
   ```bash
   --preview --preview-rows 5
   ```
   Check actual outputs before processing full dataset.

**Note**: Even with strict prompts, string fields may return unexpected values. Consider post-processing for production use.

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
uv run pytest --cov=llman --cov-report=html
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
- Supports [Google Gemini](https://ai.google.dev/), [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Groq](https://console.groq.com/), [Mistral](https://mistral.ai/), [Cohere](https://cohere.com/), and 100+ other providers exposed via LiteLLM
- Uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management
- Powered by [pandas](https://pandas.pydata.org/) for CSV processing
