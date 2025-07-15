# DEL-006 TDD Test Suite

This directory contains the comprehensive TDD (Test-Driven Development) test suite for DEL-006 "FastAPI startup validation and health checks".

## Purpose

These tests were created during the **RED phase** of TDD and are designed to drive future development of advanced validation features. They contain tests for functionality that is not yet implemented.

## Test Files

- **test_api_provider_validation.py** - Tests for individual API provider validation (Anthropic, OpenAI, Gemini, XAI)
- **test_database_validation.py** - Tests for advanced database validation (schema, permissions, migrations)
- **test_startup_events.py** - Tests for advanced startup event handling and configuration

## Why These Tests Are Separate

These tests are kept outside the main `tests/` directory because:

1. **They contain calls to unimplemented methods** like `validate_anthropic_api()`, `validate_database_schema()`, etc.
2. **They would fail CI** if run as part of the main test suite
3. **They represent future development** rather than current functionality
4. **They follow TDD RED phase** where tests are written before implementation

## Running These Tests

To run these tests (they will fail as expected):

```bash
cd del_006_tdd_tests
python -m pytest test_api_provider_validation.py -v
python -m pytest test_database_validation.py -v
python -m pytest test_startup_events.py -v
```

## Current Implementation

The **working implementation** is tested in the main test suite:

- `tests/test_settings_validation.py` - Core settings validation (5 passing tests)
- `tests/test_health_endpoints.py` - Health check endpoints (5 passing tests)

## Future Development

These TDD tests can be used to guide future implementation of:

- Individual API provider connectivity validation
- Advanced database schema and migration validation
- Enhanced startup event handling
- Performance optimization features
- Security hardening features

## TDD Methodology

This follows proper TDD methodology:

1. **🔴 RED Phase**: Write failing tests (these files)
2. **🟢 GREEN Phase**: Implement minimal functionality (current main implementation)
3. **🔧 REFACTOR Phase**: Optimize and enhance (future iterations)