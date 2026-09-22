import inspect
import os
from pathlib import Path
import pytest

import monarch.core.access as access_module
from monarch.cli import main
from monarch.core.access import (
    AccessDeniedError,
    BOSS_EMAIL,
    CREATOR_NAME,
    ENGLISH_LOCK_MESSAGE,
    EXPECTED_KEY_HASH,
    RAW_LOCK_MESSAGE,
    _key_hash,
    activate,
    deactivate,
    get_lock_banner,
    is_activated,
    require_access,
    verify_key,
)

#: Test-only key — matches tests/conftest.py, NOT the real activation key.
TEST_KEY = "monarch_test_only_key"


def test_constants():
    # No plaintext key in the module — only a 64-char hex SHA-256 hash.
    assert len(EXPECTED_KEY_HASH) == 64
    int(EXPECTED_KEY_HASH, 16)  # valid hex
    assert BOSS_EMAIL == "workadilchandio@gmail.com"
    assert "Adil" in CREATOR_NAME
    assert "Me Monarch Agent muje Adil chandio ne banaya ha" in RAW_LOCK_MESSAGE
    assert "workadilchandio@gmail.com" in RAW_LOCK_MESSAGE
    assert "workadilchandio@gmail.com" in ENGLISH_LOCK_MESSAGE


def test_no_plaintext_key_in_source():
    """Regression guard: the activation key must never be hardcoded again."""
    src = inspect.getsource(access_module)
    assert "DoitMon" not in src
    assert "MASTER_ACCESS_KEY" not in src


def test_verify_key():
    assert verify_key(TEST_KEY) is True
    assert verify_key(f" {TEST_KEY} ") is True
    assert verify_key("wrong_key") is False
    assert verify_key("") is False
    assert verify_key(None) is False


def test_activation_flow(monkeypatch, tmp_path):
    monkeypatch.delenv("MONARCH_ACCESS_KEY", raising=False)
    monkeypatch.delenv("MONARCH_KEY", raising=False)
    monkeypatch.setattr("monarch.core.access._ACTIVATION_DIR", tmp_path / ".monarch")
    monkeypatch.setattr("monarch.core.access._ACTIVATION_FILE", tmp_path / ".monarch" / ".activated")
    monkeypatch.setattr("monarch.core.access._LOCAL_KEY_FILE", tmp_path / ".monarch_key")

    # Initially not activated
    assert not is_activated()

    # Wrong key fails
    ok, banner = activate("invalid_key")
    assert not ok
    assert "workadilchandio@gmail.com" in banner
    assert not is_activated()

    # Correct key activates
    ok, msg = activate(TEST_KEY)
    assert ok
    assert "ACCESS GRANTED" in msg
    assert is_activated()

    # Activation file stores only the hash, never the plaintext key
    token = (tmp_path / ".monarch" / ".activated").read_text(encoding="utf-8")
    assert token == _key_hash(TEST_KEY)
    assert TEST_KEY not in token

    # Deactivate relocks
    deactivate()
    assert not is_activated()


def test_require_access_guard(monkeypatch, tmp_path):
    monkeypatch.delenv("MONARCH_ACCESS_KEY", raising=False)
    monkeypatch.delenv("MONARCH_KEY", raising=False)
    monkeypatch.setattr("monarch.core.access._ACTIVATION_DIR", tmp_path / ".monarch")
    monkeypatch.setattr("monarch.core.access._ACTIVATION_FILE", tmp_path / ".monarch" / ".activated")
    monkeypatch.setattr("monarch.core.access._LOCAL_KEY_FILE", tmp_path / ".monarch_key")

    # Should raise when not active and not interactive
    with pytest.raises(AccessDeniedError):
        require_access(interactive=False)

    # Passing valid key inline succeeds
    assert require_access(key_candidate=TEST_KEY, interactive=False) is True
    assert is_activated()


def test_env_hash_rotation(monkeypatch, tmp_path):
    """MONARCH_KEY_HASH lets the boss rotate keys without touching code."""
    monkeypatch.delenv("MONARCH_ACCESS_KEY", raising=False)
    monkeypatch.delenv("MONARCH_KEY", raising=False)
    monkeypatch.setattr("monarch.core.access._ACTIVATION_DIR", tmp_path / ".monarch")
    monkeypatch.setattr("monarch.core.access._ACTIVATION_FILE", tmp_path / ".monarch" / ".activated")
    monkeypatch.setattr("monarch.core.access._LOCAL_KEY_FILE", tmp_path / ".monarch_key")

    new_key = "rotated_brand_new_key"
    monkeypatch.setenv("MONARCH_KEY_HASH", _key_hash(new_key))

    assert verify_key(new_key) is True
    # Old test key no longer matches after rotation
    assert verify_key(TEST_KEY) is False
    assert require_access(key_candidate=new_key, interactive=False) is True


def test_cli_access_commands(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("MONARCH_ACCESS_KEY", raising=False)
    monkeypatch.delenv("MONARCH_KEY", raising=False)
    monkeypatch.setattr("monarch.core.access._ACTIVATION_DIR", tmp_path / ".monarch")
    monkeypatch.setattr("monarch.core.access._ACTIVATION_FILE", tmp_path / ".monarch" / ".activated")
    monkeypatch.setattr("monarch.core.access._LOCAL_KEY_FILE", tmp_path / ".monarch_key")

    # Lock agent
    assert main(["lock"]) == 0

    # Command without key fails
    assert main(["status"]) == 1

    # Activate with wrong key fails
    assert main(["activate", "wrong"]) == 1

    # Activate with right key succeeds
    assert main(["activate", TEST_KEY]) == 0

    # Now status succeeds
    assert main(["status"]) == 0

    # Lock again
    assert main(["lock"]) == 0
    assert main(["status"]) == 1

    # Status with inline key succeeds
    assert main(["status", "--key", TEST_KEY]) == 0
    assert main(["--key", TEST_KEY, "status"]) == 0
