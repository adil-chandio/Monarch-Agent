import pytest

from monarch.core.access import _key_hash

#: Test-only key — NOT the real activation key. The real key never enters the repo.
TEST_KEY = "monarch_test_only_key"


@pytest.fixture(autouse=True)
def setup_monarch_access(monkeypatch):
    """Authorize test runs with a throwaway key + its hash (never the real key)."""
    monkeypatch.setenv("MONARCH_ACCESS_KEY", TEST_KEY)
    monkeypatch.setenv("MONARCH_KEY_HASH", _key_hash(TEST_KEY))
