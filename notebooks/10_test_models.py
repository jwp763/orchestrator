# Databricks notebook source
# MAGIC %md
# MAGIC # Test Models Module
# MAGIC Run unit tests for the Pydantic models

# COMMAND ----------

import pytest

# Use -c /dev/null to ignore project pytest configuration
result = pytest.main(['-c', '/dev/null', 'tests/test_models.py'])

if result != 0:
    raise SystemExit(result)


