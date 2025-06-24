# Databricks notebook source
# MAGIC %md
# MAGIC # Test Config Module
# MAGIC Run unit tests for the settings configuration

# COMMAND ----------

import pytest

result = pytest.main(['-c', '/dev/null', 'tests/test_config.py'])

if result != 0:
    raise SystemExit(result)

