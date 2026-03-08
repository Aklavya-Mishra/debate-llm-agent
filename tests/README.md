# Tests

This directory contains tests for the debate LLM agent.

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=agents --cov=evaluator

# Run specific test file
pytest tests/test_models.py -v
```

## Test Structure

- `test_models.py` - Tests for data models and prompt templates
- `test_evaluator.py` - Tests for the evaluation metrics
- `test_api.py` - API endpoint tests (requires mock LLM)
