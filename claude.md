# LLM Analyser - Development Notes

## Project Overview

LLM Analyser is a Python-based command-line tool designed to process CSV data using Large Language Models (LLMs). The tool enables users to augment their datasets with AI-generated structured outputs by processing each row sequentially through an LLM API.

**Version 0.2.0** introduces LiteLLM integration for multi-provider support, enabling seamless switching between Gemini, OpenAI, Anthropic, and 100+ other LLM providers with enforced JSON structured output.

## Architecture

### Core Components

The project is structured into modular components for maintainability and separation of concerns:

```
llm_analyser/
├── config.py       # Configuration constants and settings
├── llm_client.py   # LLM API client with retry logic
└── processor.py    # CSV processing orchestration
```

### Design Decisions

#### 1. Sequential Processing

**Decision**: Process rows one at a time instead of parallel processing.

**Rationale**:
- API rate limits are the primary bottleneck, not CPU
- Simplifies error handling and recovery
- Reduces risk of rate limit violations
- Makes progress tracking more straightforward
- Lower memory footprint for large datasets

**Trade-off**: Slower processing, but more reliable and cost-effective.

#### 2. Interactive Prompt Input

**Decision**: Collect analysis prompts interactively rather than via command-line arguments.

**Rationale**:
- Prompts can be long and complex
- Shell escaping for multi-line prompts is error-prone
- Better user experience for iterative prompt refinement
- Cleaner command-line interface

**Alternative Considered**: Config file-based prompts (rejected for initial version to keep it simple).

#### 3. LiteLLM for Multi-Provider Support

**Decision**: Use LiteLLM instead of provider-specific SDKs.

**Rationale**:
- **Unified Interface**: Single API for 100+ LLM providers
- **JSON Mode**: Built-in `response_format={"type": "json_object"}` support
- **Provider Flexibility**: Easy to switch between providers without code changes
- **Future-Proof**: New providers are supported automatically
- **Cost Optimization**: Can easily switch to cheaper models for testing

**Trade-off**: Adds another dependency, but the benefits far outweigh the cost.

#### 4. Simple Dictionary-Based Output Schema

**Decision**: Use simple JSON dictionaries for structured output with enforced JSON mode.

**Rationale**:
- Minimal boilerplate code
- Flexible for different use cases
- LLM determines output structure based on prompt
- JSON mode ensures reliable parsing
- Easy to extend and modify
- Lower learning curve for users

**Trade-off**: Less type safety than Pydantic, but more flexibility.

#### 5. Automatic JSON Parsing with Cleanup

**Decision**: Use JSON mode + automatic cleanup of markdown code blocks.

**Rationale**:
- JSON mode (`response_format={"type": "json_object"}`) enforces JSON output
- Fallback cleanup handles edge cases where LLMs still add markdown
- Improves reliability without requiring perfect prompt engineering
- Transparent to users
- Handles common formatting variations

**Note**: JSON mode is natively supported by OpenAI and Gemini. LiteLLM handles other providers gracefully.

## API Client Design

### LiteLLM Integration

The `LLMClient` uses LiteLLM's `completion()` function for unified multi-provider access:

```python
response = completion(
    model=self.model_name,
    messages=[...],
    response_format={"type": "json_object"}  # Enforced JSON mode
)
```

**Key Features**:
- **Provider Detection**: Automatically detects provider from model name
- **API Key Management**: Uses standard environment variables per provider
- **JSON Mode**: Enforces structured output when supported
- **Graceful Degradation**: Falls back to prompt-based JSON for unsupported providers

### Retry Strategy

The `LLMClient` uses the `tenacity` library for sophisticated retry logic:

```python
@retry(
    retry=retry_if_exception_type((
        RateLimitError,
        ServiceUnavailableError,
        APIError,
        Timeout,
    )),
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=2, min=1, max=60),
    reraise=True,
)
```

**Key Features**:
- Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
- Retries LiteLLM exception types (unified across providers)
- Maximum 5 retry attempts
- Re-raises exception if all retries exhausted

### Rate Limiting

Built-in rate limiting prevents API quota violations:

```python
def _rate_limit_delay(self):
    elapsed = time.time() - self.last_request_time
    if elapsed < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - elapsed)
```

- 0.5 second minimum delay between requests
- Configurable via `config.py`
- Applied before each API call

## CSV Processing

### Error Handling Strategy

The processor continues processing even when individual rows fail:

1. **Catch Exceptions**: Errors for individual rows are caught and logged
2. **Empty Placeholders**: Failed rows get empty dictionaries to maintain alignment
3. **Error Summary**: All errors are reported at the end
4. **Partial Success**: Successfully processed rows are saved even if some fail

**Benefits**:
- Long-running jobs don't fail completely due to single row errors
- Users can identify and manually fix problematic rows
- Better UX for large datasets

### Preview Mode

Preview mode allows users to test prompts before full processing:

```bash
uv run python main.py --input data.csv --columns col1,col2 --preview
```

**Features**:
- Processes only first N rows (default: 3)
- Shows input and output for each row
- Doesn't save to file
- Helps refine prompts before expensive full runs

## Configuration Management

### Environment Variables

API keys are managed via environment variables or `.env` files:

- **Security**: Keeps secrets out of code
- **Flexibility**: Easy to switch between dev/prod environments
- **Standard Practice**: Follows twelve-factor app methodology

### Configuration File

`config.py` centralizes all configuration:

```python
DEFAULT_MODEL = "gemini-2.0-flash-lite"
MAX_RETRIES = 5
RETRY_MIN_WAIT = 1
RETRY_MAX_WAIT = 60
REQUEST_DELAY = 0.5
```

**Benefits**:
- Single source of truth
- Easy to modify behavior without code changes
- Type-safe constants
- Well-documented settings

## Testing Considerations

### Manual Testing Strategy

For initial development, focus on manual testing:

1. **Preview Mode**: Test prompts on sample data
2. **Small Datasets**: Use small CSVs for integration testing
3. **Error Injection**: Test with invalid API keys, malformed prompts
4. **Rate Limit Testing**: Process enough rows to trigger rate limits

### Future Testing Improvements

For production use, consider:

- **Unit Tests**: Test individual components (client, processor)
- **Mock API**: Use mock LLM responses for deterministic testing
- **Integration Tests**: End-to-end tests with sample data
- **Performance Tests**: Benchmark processing speed and memory usage

## Potential Enhancements

### Short-term Improvements

1. **Resume Capability**: Save progress and resume interrupted jobs
   - Checkpoint processed rows
   - Skip already-processed rows on restart

2. **Batch Preview**: Show multiple rows side-by-side for comparison
   - Better for prompt tuning
   - Identify edge cases

3. **Custom Output Schemas**: Support Pydantic models for type safety
   - Optional feature for advanced users
   - Better validation of LLM outputs

4. **Progress Bar**: Visual progress indicator using `tqdm`
   - Estimated time remaining
   - Success/failure counts

### Long-term Enhancements

1. **Multiple LLM Support**: Add OpenAI, Anthropic, local models
   - Unified interface
   - Model comparison mode

2. **Parallel Processing**: Optional parallel mode with rate limiting
   - Semaphore-based concurrency control
   - Configurable worker count

3. **Cost Tracking**: Estimate and track API costs
   - Token counting
   - Cost per row
   - Total job cost

4. **Streaming Mode**: Process large files without loading entirely into memory
   - Chunk-based processing
   - Lower memory footprint

## Common Pitfalls and Solutions

### 1. Rate Limiting

**Problem**: API returns 429 errors despite retry logic.

**Solution**:
- Increase `REQUEST_DELAY` in config
- Reduce batch size (already at 1)
- Use a higher-tier API plan

### 2. Invalid JSON Responses

**Problem**: LLM returns text that isn't valid JSON.

**Solution**:
- Make prompt more specific about JSON requirements
- Add examples of expected output format to prompt
- Use temperature=0 for more deterministic outputs (future feature)

### 3. Long-Running Jobs

**Problem**: Processing large datasets takes too long.

**Solution**:
- Use preview mode to validate approach first
- Process in chunks (split CSV manually)
- Consider parallel processing (future feature)

### 4. Memory Issues

**Problem**: Large CSVs consume too much memory.

**Solution**:
- Use chunk-based processing (future feature)
- Process in smaller batches
- Increase available memory

## Development Workflow

### Adding a New Feature

1. **Update Config**: Add any new constants to `config.py`
2. **Implement Logic**: Add feature in appropriate module
3. **Update CLI**: Modify `main.py` to expose new options
4. **Document**: Update `README.md` with usage examples
5. **Test**: Manual testing with sample data

### Code Style

- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Google-style docstrings for all public functions
- **Error Messages**: Clear, actionable error messages
- **Logging**: Use print statements for user feedback (simple approach)

### Dependencies

Minimal dependency philosophy:
- `litellm`: Multi-provider LLM API client (replaces provider-specific SDKs)
- `pandas`: CSV processing (industry standard)
- `tenacity`: Retry logic (battle-tested)
- `python-dotenv`: Environment management (standard practice)

**Rationale**: Each dependency must provide significant value and be well-maintained. LiteLLM consolidates what would otherwise be multiple provider-specific dependencies.

## Deployment Considerations

### Distribution

Current approach: Git repository + uv

**Future Options**:
- PyPI package: `pip install llm-analyser`
- Docker container: Isolated environment
- Pre-built binaries: PyInstaller for non-Python users

### Configuration for Production

1. **API Key Management**: Use secrets manager (AWS Secrets Manager, etc.)
2. **Logging**: Replace print statements with proper logging framework
3. **Monitoring**: Add metrics and alerting
4. **Error Tracking**: Integrate with error tracking service (Sentry, etc.)

## Performance Characteristics

### Time Complexity

- **Per Row**: O(1) API call + O(m) where m is response size
- **Total**: O(n) where n is number of rows
- **Bottleneck**: API latency (typically 1-3 seconds per request)

### Space Complexity

- **Memory**: O(n) - entire DataFrame held in memory
- **Storage**: O(n * m) where m is average output size

### Typical Performance

With default settings:
- ~100-120 rows per minute
- Limited by REQUEST_DELAY (0.5s) and API latency
- ~6000-7000 rows per hour

## Security Considerations

1. **API Key Storage**: Never commit `.env` files
2. **Input Validation**: Validate column names and file paths
3. **Output Sanitization**: Be cautious with user-generated prompts
4. **Rate Limiting**: Prevents accidental cost overruns

## Maintenance Notes

### Regular Tasks

- **Dependency Updates**: Check for security updates monthly
- **API Changes**: Monitor Gemini API changelog for breaking changes
- **Cost Monitoring**: Review API usage and costs

### Known Issues

None currently. Track issues in GitHub Issues when available.

## Version History

### v0.2.0 (Current)
- **LiteLLM Integration**: Replaced `google-generativeai` with LiteLLM
- **Multi-Provider Support**: Supports Gemini, OpenAI, Anthropic, and 100+ providers
- **Enforced JSON Mode**: Uses `response_format={"type": "json_object"}`
- **Provider Auto-Detection**: Automatically detects provider from model name
- **Model Listing**: Added `--list-models` command

### v0.1.0
- Initial release with Gemini-only support
- Basic CSV processing with LLM-generated columns
- Retry logic and rate limiting
- Preview mode

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [LiteLLM Providers](https://docs.litellm.ai/docs/providers)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Tenacity Documentation](https://tenacity.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [uv Documentation](https://github.com/astral-sh/uv)
