## pplyz

Minimal CSV→LLM→CSV transformer powered by LiteLLM. Point it at a CSV, pick columns, describe the desired JSON schema, and pplyz writes the result back as new columns.

### Quick run (uvx)

```bash
# No install: pulls pplyz from PyPI / TestPyPI into an ephemeral venv
uvx pplyz --input data/sample.csv --columns question,answer --output enriched.csv
```

Add `--preview` to try a handful of rows first. Use `--list` to print bundled prompt templates.

### Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- One LLM API key supported by LiteLLM (OpenAI, Gemini, Anthropic, Groq, etc.)

### Configuration

pplyz loads configuration in this order (later wins):

1. Existing environment variables
2. `./pplyz.local.toml`
3. `~/.config/pplyz/config.toml` (override via `PPLYZ_CONFIG_DIR`)

Start from the template:

```bash
cp pplyz.local.toml.example pplyz.local.toml
```

Example config:

```toml
[env]
OPENAI_API_KEY = "sk-..."

[pplyz]
default_model = "gpt-4o-mini"
```

Only set the providers you need. Common keys: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, or `PPLYZ_DEFAULT_MODEL` to force a model string like `groq/llama-3.1-8b-instant`.

### Local development

```bash
uv sync
uv run python main.py --help
```

Pre-commit runs pytest + Ruff automatically. Use `uv tool run pre-commit install` before committing.

### Support

- Issues / PRs welcome.
- Licensed under MIT (see `LICENSE`).

```bash
pplyz --input data/yourfile.csv --columns title,abstract --preview --preview-rows 5
```

### Examples

#### Example 1: Sentiment Analysis

```bash
pplyz --input data/reviews.csv --columns review_text --output sentiment_results.csv
```

When prompted, enter:
```
Analyze the sentiment and classify as positive, negative, or neutral. Also provide a confidence score.
```

#### Example 2: Academic Paper Analysis

```bash
pplyz --input data/hsa-miR-144-3p.csv --columns title,abstract --output analysis.csv
```

When prompted, enter:
```
Extract the following information: research_topic, methodology, key_findings, and clinical_significance
```

#### Example 3: Using Different LLM Providers

```bash
# Use Gemini 2.0 Flash Lite (default)
pplyz --input data/papers.csv --columns title,abstract --output results.csv

# Use OpenAI GPT-4o
pplyz --input data/papers.csv --columns title,abstract --output results.csv --model gpt-4o

# Use Anthropic Claude 3.5 Sonnet
pplyz --input data/papers.csv --columns title,abstract --output results.csv --model claude-3-5-sonnet-20241022

# Use OpenAI GPT-4o Mini (cost-effective)
pplyz --input data/papers.csv --columns title,abstract --output results.csv --model gpt-4o-mini
```

#### Example 4: Boolean-Based Classification (Recommended)

```bash
pplyz \
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
pplyz --list
```

### Command-Line Options

| Option | Short | Description | Required |
|--------|-------|-------------|----------|
| `--input` | `-i` | Path to input CSV file | Yes |
| `--columns` | `-c` | Comma-separated list of columns to use as LLM input | Yes |
| `--fields` | `-f` | Field definition string (e.g., `"field1:str,field2:int"`). Required to keep output columns consistent. | Yes |
| `--output` | `-o` | Path to output CSV file (defaults to overwriting the input file when omitted) | No |
| `--model` | `-m` | LLM model name (default: `PPLYZ_DEFAULT_MODEL` or `gemini/gemini-2.5-flash-lite`) | No |
| `--list` | `-l` | List supported models and exit | No |
| `--preview` | `-p` | Preview results on sample rows without saving | No |
| `--preview-rows` | | Number of rows to preview (default: 3) | No |
| `--no-resume` | `-R` | Reprocess all rows even if output exists | No |

> **Note:** When `--output` is omitted, the processor overwrites the input CSV in place. Use `--preview` first or point `--output` to a different file if you want to keep the original rows untouched.

## Best Practices for Field Definitions

### Defining Fields

Use `--fields` (required) to describe the JSON structure you expect back. The CLI enforces this flag to keep output columns consistent:

```bash
--fields "is_relevant:bool,summary:str,keywords:list[str]"
```

Any field without `:type` defaults to `str`. Supported types: `bool`, `int`, `float`, `str`, `list[str]`, `list[int]`, `list[float]`, `list[bool]`, and `dict`.

### Field Design Patterns

#### Pattern 1: Binary Classification (Most Reliable) ✅

Use **boolean fields** for yes/no decisions - these are strictly enforced across all LLM providers:

```bash
pplyz \
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

For the full list, run `pplyz --list` (or `-l`) (use `uv run python main.py --list` from source) or visit [LiteLLM Providers](https://docs.litellm.ai/docs/providers).

## Configuration

Key configuration options can be found in `pplyz/config.py` and `pplyz/settings.py`:

- `DEFAULT_MODEL`: Default model (gemini/gemini-2.5-flash-lite). Override by setting `PPLYZ_DEFAULT_MODEL` in your config TOML or environment.
- `USE_JSON_MODE`: Force JSON output via LiteLLM (True)
- `MAX_RETRIES`: Maximum number of retry attempts (`len(RETRY_BACKOFF_SCHEDULE) + 1`)
- `RETRY_BACKOFF_SCHEDULE`: Fixed delays between retries (`[1, 2, 3, 5, 10, 10, 10, 10, 10]` seconds)
- `REQUEST_DELAY`: Delay between API requests (0.5 seconds)
- `pplyz/settings.py`: Resolves user-level configuration from `~/.config/pplyz/`

## Project Structure

```
pplyz/
├── main.py                 # Dev entry point (calls pplyz.cli)
├── pplyz/
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Static configuration settings
│   ├── llm_client.py      # LLM API client with retry logic
│   ├── processor.py       # CSV processing logic
│   ├── schemas.py         # Output schema definitions
│   ├── settings.py        # Runtime configuration loader
│   └── utils.py           # Shared helpers
├── data/                   # Input CSV files
├── pyproject.toml         # Project dependencies
├── pplyz.local.toml.example # Example local configuration
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

**Solution**: Make sure you've set the appropriate API key in `pplyz.local.toml`, `~/.config/pplyz/config.toml`, or as an environment variable.

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
uv run pytest --cov=pplyz --cov-report=html
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
