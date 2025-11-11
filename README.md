[![PyPI Downloads](https://static.pepy.tech/personalized-badge/pplyz?period=total&units=international_system&left_color=grey&right_color=green&left_text=downloads)](https://pepy.tech/projects/pplyz)

# pplyz

Minimal CSV→LLM→CSV transformer powered by LiteLLM and uv. 日本語はこちら → [README.ja.md](README.ja.md)

## Requirements

- [uv](https://github.com/astral-sh/uv)
  - macOS/Linux: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `scoop install uv`
- At least one LiteLLM-compatible API key (OpenAI, Gemini, Anthropic, Groq, etc.)

`uvx` downloads the right Python runtime automatically, so no global Python is needed once uv is installed.

## Quick run (uvx)

```bash
uvx pplyz \
  --input data/sample.csv \
  --columns question,answer \
  --fields 'score:int,notes:str' \
  --output enriched.csv
```

- `--preview --preview-rows 5` dry-runs a handful of rows.
- `--list` prints bundled prompt templates and exits.
- `--model provider/name` overrides the LiteLLM model (e.g., `groq/llama-3.1-8b-instant`).

Run `uvx pplyz --help` for every flag.

## Common options

| Flag | Description | Required |
| --- | --- | --- |
| `-i, --input PATH` | Input CSV. | Yes |
| `-c, --columns title,abstract` | Comma-separated columns passed to the LLM. | Yes |
| `-f, --fields 'score:int,notes:str'` | Output schema. Types: `bool`, `int`, `float`, `str`, `list[...]`, `dict`. Missing `:type` defaults to `str`. | Yes |
| `-o, --output PATH` | Output CSV (defaults to overwriting the input file). | No |
| `-p, --preview` | Process a few rows and show would-be output without writing. | No |
| `--preview-rows N` | Number of preview rows (default 3). | No |
| `-m, --model provider/name` | LiteLLM model (default `gemini/gemini-2.5-flash-lite`). | No |
| `-R, --no-resume` | Disable resume mode; always recompute rows. | No |
| `-l, --list` | List supported templates/models and exit. | No |

## Configuration

1. Create the user config once:

   ```bash
   mkdir -p ~/.config/pplyz
   $EDITOR ~/.config/pplyz/config.toml
   ```

2. Add only the providers you actually use:

   ```toml
   [env]
   OPENAI_API_KEY = "sk-..."
   GROQ_API_KEY = "gsk-..."

   [pplyz]
   default_model = "gpt-4o-mini"
   ```

3. At runtime pplyz loads settings in this order: environment variables → `~/.config/pplyz/config.toml`. To keep configs elsewhere, set `PPLYZ_CONFIG_DIR=/path/to/dir` and place `config.toml` there.

### Settings reference

**[pplyz] table**

| key | description | default |
| --- | --- | --- |
| `default_model` | Sets the fallback LiteLLM model when `--model` is omitted. | `gemini/gemini-2.5-flash-lite` |

### Provider API keys

Set these inside the `[env]` table of your `config.toml`:

| Provider | Keys (checked in order) |
| --- | --- |
| Gemini | `GEMINI_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic / Claude | `ANTHROPIC_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| Cohere | `COHERE_API_KEY` |
| Replicate | `REPLICATE_API_KEY` |
| Hugging Face | `HUGGINGFACE_API_KEY` |
| Together AI | `TOGETHERAI_API_KEY`, `TOGETHER_AI_TOKEN` |
| Perplexity | `PERPLEXITY_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| xAI | `XAI_API_KEY` |
| Azure OpenAI | `AZURE_OPENAI_API_KEY`, `AZURE_API_KEY` |
| AWS (Bedrock/SageMaker) | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| Vertex AI | `GOOGLE_APPLICATION_CREDENTIALS` |

## Supported models

Pulled from `pplyz/config.py` for quick reference—LiteLLM supports many more.

| Model id | Notes |
| --- | --- |
| `gemini/gemini-2.5-flash-lite` | Default, fast + cheap. |
| `gemini/gemini-1.5-pro` | Higher quality Gemini. |
| `gpt-4o` | OpenAI flagship. |
| `gpt-4o-mini` | Cheaper GPT-4o Mini. |
| `claude-3-5-sonnet-20241022` | Balanced Anthropic model. |
| `claude-3-haiku-20240307` | Fast Anthropic Haiku. |
| `groq/llama-3.1-8b-instant` | Ultra-low latency on Groq. |
| `mistral/mistral-large-latest` | Enterprise Mistral. |
| `cohere/command-r-plus` | Tool-friendly Cohere model. |
| `replicate/meta/meta-llama-3-8b-instruct` | Replicate-hosted Llama 3 8B. |
| `huggingface/meta-llama/Meta-Llama-3-8B-Instruct` | Hugging Face endpoint. |
| `xai/grok-beta` | xAI Grok Beta. |
| `together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo` | Together AI aggregator. |
| `perplexity/llama-3.1-sonar-small-128k-online` | Web-augmented Perplexity Sonar. |
| `deepseek/deepseek-chat` | DeepSeek Chat. |
| `azure/gpt-4o` | Azure OpenAI variant. |
| `databricks/mixtral-8x7b-instruct` | Databricks MosaicML endpoint. |
| `sagemaker/meta-textgeneration-llama-3-8b` | AWS SageMaker endpoint. |

Use `uvx pplyz --list` to see the live list bundled with your version.

## Examples

Sentiment pass with a preview first:

```bash
uvx pplyz \
  --input data/reviews.csv \
  --columns review_text \
  --fields 'sentiment:str,confidence:float' \
  --preview --preview-rows 5
```

Boolean classifier that writes back into the same CSV:

```bash
uvx pplyz \
  --input data/articles.csv \
  --columns title,abstract \
  --fields 'is_relevant:bool,summary:str' \
  --output data/articles.csv
```

Model override with Anthropic:

```bash
uvx pplyz \
  --input data/papers.csv \
  --columns title,abstract \
  --fields 'findings:str' \
  --model claude-3-5-sonnet-20241022
```

## Tips

- Boolean fields keep binary classifiers deterministic (`true`/`false`).
- Keep prompts short and explicit about the JSON schema you expect to avoid parsing errors.
- Use `--preview` before long or expensive CSV batches to validate prompts and model choice.

## Support & License

Issues and PRs are welcome. Licensed under MIT — see `LICENSE`.
