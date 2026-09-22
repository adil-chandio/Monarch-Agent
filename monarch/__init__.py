"""Monarch — faceless YouTube intelligence. Gates, maths, states are real."""

from monarch.core.access import (
    AccessDeniedError,
    activate,
    deactivate,
    is_activated,
    require_access,
    verify_key,
)
from monarch.core.fountain import Screenplay, parse, parse_file
from monarch.pipelines.fountain import (
    FountainBeat,
    ScriptReport,
    beats_from_lines,
    beats_from_screenplay,
    build_script,
    write_fountain,
)

__version__ = "0.1.0"

__all__ = [
    "AccessDeniedError",
    "FountainBeat",
    "Screenplay",
    "ScriptReport",
    "__version__",
    "activate",
    "beats_from_lines",
    "beats_from_screenplay",
    "build_script",
    "deactivate",
    "is_activated",
    "parse",
    "parse_file",
    "require_access",
    "verify_key",
    "write_fountain",
]
