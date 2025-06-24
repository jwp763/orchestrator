# Databricks notebook source
# MAGIC %md
# MAGIC # Test Integrations Module
# MAGIC Run unit tests for available integrations

# COMMAND ----------

import pytest

result = pytest.main(['-c', '/dev/null', 'tests/test_integrations'])

if result != 0:
    raise SystemExit(result)

