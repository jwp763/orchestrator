# Databricks notebook source
# MAGIC %md
# MAGIC # Test Agent Module
# MAGIC Run unit tests for the orchestrator agent

# COMMAND ----------

import pytest

result = pytest.main(['-c', '/dev/null', 'tests/test_agent.py'])

if result != 0:
    raise SystemExit(result)


