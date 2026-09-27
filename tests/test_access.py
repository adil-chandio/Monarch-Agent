import os
from pathlib import Path
import pytest

from monarch.cli import main
from monarch.core.access import (
    AccessDeniedError,
    BOSS_EMAIL,
    CREATOR_NAME,
    ENGLISH_LOCK_MESSAGE,
    MASTER_ACCESS_KEY,
    RAW_LOCK_MESSAGE,
    activate,
    deactivate,
    get_lock_banner,
    is_activated,
    require_access,
    verify_key,
)


def test_constants():
    assert MASTER_ACCESS_KEY == "DoitMon@rch"
    assert BOSS_EMAIL == "workadilchandio@gmail.com"
    assert "Adil" in CREATOR_NAME
    assert "Me Monarch Agent muje Adil chandio ne banaya ha" in RAW_LOCK_MESSAGE
    assert "workadilchandio@gmail.com" in RAW_LOCK_MESSAGE
    assert "workadilchandio@gmail.com" in ENGLISH_LOCK_MESSAGE


def test_verify_key():
    assert verify_key("DoitMon@rch") is True
    assert verify_key(" DoitMon@rch ") is True
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
    ok, msg = activate("DoitMon@rch")
    assert ok
    assert "ACCESS GRANTED" in msg
    assert is_activated()

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
    assert require_access(key_candidate="DoitMon@rch", interactive=False) is True
    assert is_activated()


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
    assert main(["activate", "DoitMon@rch"]) == 0

    # Now status succeeds
    assert main(["status"]) == 0

    # Lock again
    assert main(["lock"]) == 0
    assert main(["status"]) == 1

    # Status with inline key succeeds
    assert main(["status", "--key", "DoitMon@rch"]) == 0
    assert main(["--key", "DoitMon@rch", "status"]) == 0
