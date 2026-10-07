from __future__ import annotations

import pytest

from monarch.cli import main


def test_cli_runs_without_activation(monkeypatch, capsys):
    monkeypatch.delenv("MONARCH_ACCESS_KEY", raising=False)
    monkeypatch.delenv("MONARCH_KEY", raising=False)

    assert main(["status"]) == 0
    assert '"agent": "monarch"' in capsys.readouterr().out

    assert main(["maths", "--seconds", "42"]) == 0
    assert "42s" in capsys.readouterr().out


def test_help_has_no_activation_or_lock_commands(capsys):
    assert main([]) == 0
    help_text = capsys.readouterr().out.lower()
    assert "activate" not in help_text
    assert "lock" not in help_text
    assert "--key" not in help_text


def test_removed_activation_switches_are_rejected():
    for args in (["activate"], ["lock"], ["--key", "status"]):
        with pytest.raises(SystemExit) as exc:
            main(list(args))
        assert exc.value.code == 2
