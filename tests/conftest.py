import os
import pytest

@pytest.fixture(autouse=True)
def setup_monarch_access(monkeypatch):
    """Ensure all test runs have valid access authorization."""
    monkeypatch.setenv("MONARCH_ACCESS_KEY", "DoitMon@rch")
