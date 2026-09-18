"""Pytest configuration and fixtures."""
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "acceptance: marks tests that require full pipeline (API key + ingested KB)"
    )
