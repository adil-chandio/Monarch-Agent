from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
import sys

#: SHA-256 of the *salted* master activation key.
#:
#: SECURITY LAW: the plaintext key is NEVER stored in this repository.
#: Only this hash lives here, so cloning the repo reveals nothing usable.
#: To rotate the key, set the MONARCH_KEY_HASH environment variable to the
#: hash of the new key (or update this constant) — never commit plaintext.
EXPECTED_KEY_HASH = (
    "7f01e68aaab310504862f0c63872699e8743298ee162ab065c98297d59aafe3b"
)

#: Creator and Contact Info
CREATOR_NAME = "Adil Chandio"
BOSS_EMAIL = "workadilchandio@gmail.com"

#: Exact lock message requested by Creator
RAW_LOCK_MESSAGE = (
    "Me Monarch Agent muje Adil chandio ne banaya ha to apko mujhe access run Karne "
    "ke Liye key chaiye Yahan chat me key dalen Aage key NAHI ha to apko mere boss "
    f"se milegi unka contact Gmail: {BOSS_EMAIL}"
)

ENGLISH_LOCK_MESSAGE = (
    f"I am Monarch Agent, created by {CREATOR_NAME}. To access and run me, you need "
    f"an activation key. Please enter the key in the chat. If you don't have the key, "
    f"you can get it from my boss. Contact Gmail: {BOSS_EMAIL}"
)

_ACTIVATION_DIR = Path.home() / ".monarch"
_ACTIVATION_FILE = _ACTIVATION_DIR / ".activated"
_LOCAL_KEY_FILE = Path(".monarch_key")


def _key_hash(key: str) -> str:
    """Generate SHA-256 hash for key verification/storage."""
    return hashlib.sha256(f"monarch_salt_{key}".encode("utf-8")).hexdigest()


def _expected_hash() -> str:
    """Expected key hash — env override (MONARCH_KEY_HASH) wins for rotation."""
    return os.environ.get("MONARCH_KEY_HASH", EXPECTED_KEY_HASH).strip().lower()


def get_lock_banner() -> str:
    """Return formatted visual lock banner with creator credit and contact."""
    width = 75
    border = "═" * width
    line = "─" * width
    return (
        f"\n╔{border}╗\n"
        f"║{'🔒 MONARCH AGENT — ACCESS LOCKED':^{width}}║\n"
        f"║{'Created by Adil Chandio':^{width}}║\n"
        f"╠{border}╣\n"
        f"\n{RAW_LOCK_MESSAGE}\n\n"
        f"{line}\n"
        f"[ENGLISH NOTICE]:\n"
        f"{ENGLISH_LOCK_MESSAGE}\n"
        f"╚{border}╝\n"
    )


def verify_key(candidate: str | None) -> bool:
    """Verify a candidate key against the stored hash (constant-time compare)."""
    if not candidate:
        return False
    candidate_hash = _key_hash(candidate.strip())
    return hmac.compare_digest(candidate_hash, _expected_hash())


def is_activated() -> bool:
    """
    Check if Monarch Agent is currently activated via:
    1. Environment variable `MONARCH_ACCESS_KEY` or `MONARCH_KEY`
    2. Stored activation token in ~/.monarch/.activated
    3. Project root .monarch_key file
    """
    # 1. Environment variables
    env_key = os.environ.get("MONARCH_ACCESS_KEY") or os.environ.get("MONARCH_KEY")
    if env_key and verify_key(env_key):
        return True

    expected = _expected_hash()

    # 2. Global activation file
    try:
        if _ACTIVATION_FILE.is_file():
            content = _ACTIVATION_FILE.read_text(encoding="utf-8").strip().lower()
            if hmac.compare_digest(content, expected):
                return True
    except Exception:
        pass

    # 3. Local project key file (plaintext key or stored hash)
    try:
        if _LOCAL_KEY_FILE.is_file():
            content = _LOCAL_KEY_FILE.read_text(encoding="utf-8").strip()
            if verify_key(content) or hmac.compare_digest(content.lower(), expected):
                return True
    except Exception:
        pass

    return False


def activate(key: str, persistent: bool = True) -> tuple[bool, str]:
    """
    Attempt to activate Monarch Agent using the provided key.
    If valid and persistent=True, saves only the key's *hash* as the token.
    """
    if not verify_key(key):
        return False, get_lock_banner()

    if persistent:
        token = _key_hash(key.strip())
        try:
            _ACTIVATION_DIR.mkdir(parents=True, exist_ok=True)
            _ACTIVATION_FILE.write_text(token, encoding="utf-8")
        except Exception:
            # Fallback to local file if home dir is not writable
            try:
                _LOCAL_KEY_FILE.write_text(token, encoding="utf-8")
            except Exception:
                pass

    msg = (
        f"\n✅ [ACCESS GRANTED] Monarch Agent Activated Successfully!\n"
        f"👑 Welcome to Monarch Agent — Created by {CREATOR_NAME}.\n"
    )
    return True, msg


def deactivate() -> bool:
    """Remove persistent activation tokens (relock Monarch Agent)."""
    removed = False
    try:
        if _ACTIVATION_FILE.is_file():
            _ACTIVATION_FILE.unlink()
            removed = True
    except Exception:
        pass
    try:
        if _LOCAL_KEY_FILE.is_file():
            _LOCAL_KEY_FILE.unlink()
            removed = True
    except Exception:
        pass
    return removed


class AccessDeniedError(PermissionError):
    """Raised when access to Monarch Agent is denied."""
    pass


def require_access(
    key_candidate: str | None = None,
    interactive: bool = True,
) -> bool:
    """
    Enforce Monarch Agent access control.
    If key is valid or agent is activated, returns True.
    Otherwise prompts interactively (if stdin is a tty and interactive=True),
    or prints the lock banner and raises AccessDeniedError.
    """
    if key_candidate and verify_key(key_candidate):
        activate(key_candidate, persistent=True)
        return True

    if is_activated():
        return True

    # Interactive prompt if terminal is available
    if interactive and sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
        print(get_lock_banner(), file=sys.stderr)
        try:
            entered = input("🔑 Enter Monarch Access Key: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled.", file=sys.stderr)
            raise AccessDeniedError("Authentication cancelled.")

        ok, msg = activate(entered, persistent=True)
        if ok:
            print(msg, file=sys.stderr)
            return True
        else:
            print("\n❌ [ACCESS DENIED] Invalid Key!", file=sys.stderr)
            print(RAW_LOCK_MESSAGE, file=sys.stderr)
            raise AccessDeniedError("Invalid access key provided.")

    # Non-interactive failure
    print(get_lock_banner(), file=sys.stderr)
    raise AccessDeniedError(RAW_LOCK_MESSAGE)
