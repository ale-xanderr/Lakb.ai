# QUICKTEST Guide
# LAKb.ai Testing Quick Start Guide

## Current Test Status

**As of December 10, 2025:**
- **125 tests passing** (85.0%)
- 22 tests failing (15.0%)
- **147 total tests** across 14 test files
- Target: 70% coverage for core non-UI logic ✅ **MET**
- Test Duration: 20.36s
- **All 121 unit tests passing** (100%) 

> **📊 For detailed test results, coverage metrics, and comprehensive analysis, see [Test Report](./Report.md)**


## Overview

This document provides a quick reference for running tests in the LAKb.ai project. The test suite covers core business logic, services, and integration flows while excluding UI components.

### Test Categories

- **Unit Tests**: Individual service and utility function tests
- **Integration Tests**: End-to-end workflow tests
- **State Tests**: State management and controller tests
- **Async Tests**: Asynchronous API and service tests

## Prerequisites

### Required Dependencies

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio httpx-mock
```

### Environment Setup

Or install all project dependencies including testing requirements:

```bash
pip install -e .
```

### Verify Installation

```bash
pytest --version
```

You should see pytest version 7.0 or higher.

---

## Quick Start

### Run All Tests

From the project root directory:

```bash
# Using the test runner script
python tests/run_all_tests.py

# Or directly with pytest
pytest tests/
```

### Run with Coverage

```bash
# Using the test runner
python tests/run_all_tests.py --html

# Or directly with pytest
pytest --cov=src --cov-report=html
```

View the HTML coverage report:
```bash
# Open in browser
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html   # Linux
start htmlcov/index.html   # Windows
```

---

## Running Tests

### Selective Test Execution

#### By Test Type

```bash
# Unit tests only
python tests/run_all_tests.py --unit

# Integration tests only
python tests/run_all_tests.py --integration
```

#### By Test File

```bash
# Run specific test file
python tests/run_all_tests.py --file tests/test_api_service.py

# Or with pytest directly
pytest tests/test_api_service.py
```

#### By Test Function

```bash
# Run specific test function
pytest tests/test_api_service.py::TestAPIService::test_search_places_success

# Run all tests in a class
pytest tests/test_api_service.py::TestAPIService
```

#### By Marker

```bash
# Run tests with specific markers
pytest -m unit              # All unit tests
pytest -m integration       # All integration tests
pytest -m "auth"           # All auth-related tests
pytest -m "not slow"       # Exclude slow tests
```

### Verbose Output

```bash
# More detailed output
python tests/run_all_tests.py --verbose

# Or with pytest
pytest -vv
```

### Without Coverage

```bash
# Skip coverage reporting for faster execution
python tests/run_all_tests.py --no-coverage
```

---

## Understanding Coverage Reports

### Terminal Output

After running tests with coverage, you'll see a report like:

```
---------- coverage: platform linux, python 3.11.0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/core/config.py                   45      2    96%   156-157
src/services/api_service.py         120      8    93%   245-252
src/services/auth_service.py         95      5    95%   389-393
src/services/favorites_service.py    78      3    96%   201-203
---------------------------------------------------------------
TOTAL                               1250     48    96%
```

**Key Metrics:**
- **Stmts**: Total statements in the file
- **Miss**: Statements not covered by tests
- **Cover**: Percentage coverage
- **Missing**: Line numbers not covered

### Coverage Goals

As per **APPDEV_INSTRUCTIONS.md**, we target:

- **≥70% coverage** of core non-UI logic
- **Excluded from coverage**: `src/views/`, `src/main.py`, `src/views/components/`

### HTML Report

The HTML report provides interactive browsing:

1. **Index Page**: Overview of all modules with coverage percentages
2. **File View**: Line-by-line highlighting showing covered (green) and uncovered (red) code
3. **Filtering**: Sort by coverage, filename, or statements

---

## Test Organization

### Directory Structure

```
tests/
├── __init__.py                   # Package marker
├── conftest.py                   # Shared fixtures and configuration
├── pytest.ini                    # Pytest settings
├── run_all_tests.py              # All-in-one test runner
│
├── test_api_service.py           # APIService unit tests
├── test_auth_service.py          # AuthService unit tests
├── test_favorites_service.py     # FavoritesService unit tests
├── test_geolocation_service.py   # GeolocationService unit tests
├── test_profile_service.py       # ProfileService unit tests
├── test_ai_engine.py             # AIEngine unit tests
├── test_config.py                # Config unit tests
├── test_state_controllers.py     # State controller unit tests
│
├── test_auth_flow.py             # Authentication integration tests
├── test_favorites_flow.py        # Favorites workflow integration tests
└── test_places_flow.py           # Places search integration tests
```

### Test Types

#### Unit Tests

- **Purpose**: Test individual functions/methods in isolation
- **Marker**: `@pytest.mark.unit`
- **Dependencies**: All external dependencies mocked
- **Speed**: Fast (< 1s per test typically)

**Example:**
```python
@pytest.mark.unit
def test_reverse_geocode_success(mock_get, api_service):
    # Test single function with mocked HTTP call
    mock_response = Mock()
    mock_response.json.return_value = {...}
    mock_get.return_value = mock_response
    
    result = api_service.reverse_geocode(13.621, 123.194)
    
    assert result == "Expected City"
```

#### Integration Tests

- **Purpose**: Test complete workflows across multiple components
- **Marker**: `@pytest.mark.integration`
- **Dependencies**: Services interact but external APIs still mocked
- **Speed**: Moderate (1-5s per test)

**Example:**
```python
@pytest.mark.integration
def test_search_and_favorite_flow(services):
    # Test complete user workflow
    results = services["api"].search_places(query="restaurant")
    place = results["results"][0]
    services["favorites"].add_favorite(place)
    
    assert services["favorites"].is_favorite(place["place_id"])
```

---

## Mocking Strategy

### Why Mock?

- **Speed**: Tests run in milliseconds instead of seconds
- **Reliability**: No network dependencies or rate limits
- **API Keys**: No API keys required to run tests
- **Determinism**: Consistent results every time

### Common Mocks

#### Supabase Client

```python
@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with common methods."""
    client = Mock()
    client.auth = Mock()
    client.auth.get_user = Mock(return_value=Mock(user=None))
    client.table = Mock()
    return client
```

#### HTTP Requests

```python
@patch('httpx.get')
def test_api_call(mock_get, api_service):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "value"}
    mock_get.return_value = mock_response
    
    result = api_service.some_method()
```

#### Flet Page Object

```python
@pytest.fixture
def mock_page():
    """Mock Flet Page object."""
    page = Mock()
    page.client_storage = Mock()
    page.overlay = []
    return page
```

### Available Fixtures

All shared fixtures are in `tests/conftest.py`:

- `mock_page` - Flet page object
- `mock_supabase_client` - Supabase client
- `mock_supabase_user` - Authenticated user
- `mock_supabase_session` - User session
- `mock_google_places_response` - Google Places API response
- `mock_place_details_response` - Place details response
- `mock_weather_response` - Weather API response
- `mock_gemini_response` - Gemini AI response
- `sample_place_data` - Sample place data
- `sample_favorites_list` - Sample favorites

---

## Adding New Tests

### Creating a New Test File

1. **Create file** in `tests/` with prefix `test_`
2. **Import pytest** and required modules
3. **Add markers** for test categorization
4. **Use fixtures** from `conftest.py`

**Template:**
```python
"""
Unit tests for NewService.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.new_service import NewService


@pytest.mark.unit
class TestNewService:
    """Test suite for NewService."""
    
    @pytest.fixture
    def new_service(self):
        """Create service instance for testing."""
        return NewService()
    
    def test_some_method(self, new_service):
        """Test some_method does what it should."""
        result = new_service.some_method()
        
        assert result is not None
```

### Test Naming Conventions

- **Files**: `test_<module_name>.py`
- **Classes**: `Test<ClassName>`
- **Functions**: `test_<what_is_being_tested>`

**Examples:**
- `test_initialization` - Test object initialization
- `test_get_user_when_authenticated` - Test specific scenario
- `test_add_favorite_handles_duplicate` - Test error handling

### Writing Effective Tests

**Good test characteristics:**

1. **Arrange-Act-Assert** pattern
   ```python
   def test_example():
       # Arrange: Set up test data
       service = MyService()
       data = {"key": "value"}
       
       # Act: Execute the function
       result = service.process(data)
       
       # Assert: Verify the outcome
       assert result == expected_value
   ```

2. **Test one thing** - Each test should verify one behavior
3. **Clear names** - Test name should describe what it tests
4. **Independent** - Tests should not depend on each other
5. **Fast** - Mock external dependencies

---

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov pytest-mock pytest-asyncio
    
    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-fail-under=70
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
test:
  image: python:3.11
  script:
    - pip install -e .
    - pip install pytest pytest-cov pytest-mock pytest-asyncio
    - pytest --cov=src --cov-report=term --cov-fail-under=70
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Run pytest from project root:
```bash
cd /path/to/lakb.ai
pytest tests/
```

#### Fixture Not Found

**Problem**: `fixture 'mock_page' not found`

**Solution**: Ensure `conftest.py` is in the `tests/` directory and pytest can discover it.

#### Coverage Too Low

**Problem**: Coverage below 70%

**Solution**: 
1. Check which files have low coverage:
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```
2. Focus on testing files in `src/services/` and `src/state/`
3. UI files (`src/views/`) are excluded from requirements

#### Tests Timing Out

**Problem**: Tests hang or timeout

**Solution**:
- Ensure all async operations are properly mocked
- Check for infinite loops in mocked callbacks
- Use `pytest --timeout=10` to set timeout limit

#### Mock Not Working

**Problem**: Real API calls being made instead of mocks

**Solution**:
- Verify patch path is correct (use import path, not file path)
- Ensure patch is applied before the import
- Use `@patch.object()` for class methods

### Getting Help

- **Check test output**: Use `-vv` for verbose details
- **Run single test**: Isolate the failing test
- **Print debugging**: Use `print()` or `pytest -s` to show output
- **Check fixtures**: Verify fixtures are properly configured in `conftest.py`

---

## Best Practices

✅ **Do:**
- Write tests for all new features
- Keep tests simple and focused
- Use descriptive test names
- Mock external dependencies
- Aim for high coverage of business logic

❌ **Don't:**
- Test implementation details
- Make tests depend on each other
- Use real API keys in tests
- Skip error case testing
- Leave tests commented out

---

## Quick Reference

### Common Commands

```bash
# Run all tests
python tests/run_all_tests.py

# Run with HTML coverage
python tests/run_all_tests.py --html

# Run unit tests only
python tests/run_all_tests.py --unit

# Run specific file
python tests/run_all_tests.py --file tests/test_api_service.py

# Run without coverage
python tests/run_all_tests.py --no-coverage

# Verbose output
python tests/run_all_tests.py --verbose
```

### Pytest Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.state` - State controller tests
- `@pytest.mark.slow` - Slow-running tests

---

**Last Updated**: 2025-12-09  
**Project**: LAKb.ai Testing Infrastructure  
**Coverage Goal**: ≥70% of core non-UI logic
