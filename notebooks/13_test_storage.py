# Databricks notebook source
# MAGIC %md
# MAGIC # Test Storage Module
# MAGIC Run unit tests for DeltaManager and StateManager

# COMMAND ----------

import pytest

result = pytest.main(['-c', '/dev/null', 'tests/test_storage.py'])

if result != 0:
    raise SystemExit(result)

