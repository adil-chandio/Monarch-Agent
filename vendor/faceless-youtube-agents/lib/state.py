import json
import time
from pathlib import Path
from datetime import datetime

from lib.config import STATE_DIR, OUTPUTS_DIR


def create_run(title: str, mode: str, style: str, voice: str, channel_url: str = "") -> dict:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _slugify(title)
    run_id = f"{timestamp}_{slug}"

    run_dir = OUTPUTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "slides").mkdir(exist_ok=True)
    (run_dir / "audio").mkdir(exist_ok=True)

    run_state = {
        "run_id": run_id,
        "title": title,
        "mode": mode,
        "style": style,
        "voice": voice,
        "channel_url": channel_url,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "stages": {
            "slides_json": {"status": "pending"},
            "images": {"status": "pending"},
            "tts": {"status": "pending"},
            "assembly": {"status": "pending"},
            "thumbnail": {"status": "pending"},
            "upload": {"status": "pending"},
        },
        "slide_assets": {},
        "output_dir": str(run_dir),
    }

    _save_state(run_id, run_state)
    return run_state


def load_run(run_id: str) -> dict:
    state_file = STATE_DIR / f"{run_id}.json"
    with open(state_file) as f:
        return json.load(f)


def update_stage(run_id: str, stage: str, status: str, output: str = "") -> dict:
    state = load_run(run_id)
    state["stages"][stage]["status"] = status
    if output:
        state["stages"][stage]["output"] = output
    state["stages"][stage]["updated_at"] = datetime.now().isoformat()
    _save_state(run_id, state)
    return state


def update_run(run_id: str, updates: dict) -> dict:
    state = load_run(run_id)
    state.update(updates)
    _save_state(run_id, state)
    return state


def set_slide_asset(run_id: str, slide_num: int, asset_type: str, path: str) -> dict:
    state = load_run(run_id)
    key = str(slide_num)
    if key not in state["slide_assets"]:
        state["slide_assets"][key] = {}
    state["slide_assets"][key][asset_type] = path
    _save_state(run_id, state)
    return state


def list_runs(status_filter: str = "") -> list:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    runs = []
    for f in sorted(STATE_DIR.glob("*.json"), reverse=True):
        with open(f) as fh:
            state = json.load(fh)
            if not status_filter or state.get("status") == status_filter:
                runs.append(state)
    return runs


def _save_state(run_id: str, state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_file = STATE_DIR / f"{run_id}.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = "".join(c if c.isalnum() or c in (" ", "-") else "" for c in slug)
    slug = slug.replace(" ", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:50].strip("-")
