from __future__ import annotations

from monarch.core.config import secrets
from monarch.core.missing import missing
from monarch.intel.http import post_json

MODELS = (
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
)


def generate(prompt: str, system: str = "") -> str:
    key = secrets().gemini
    if not key:
        raise ValueError(missing("GEMINI_API_KEY in .env"))
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    body: dict = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    last = None
    for model in MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={key}"
        )
        try:
            data = post_json(url, body)
        except RuntimeError as e:
            last = e
            continue
        cands = data.get("candidates") or []
        if not cands:
            last = RuntimeError(str(data)[:300])
            continue
        parts = cands[0].get("content", {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
        if text.strip():
            return text
    raise RuntimeError(last or "gemini empty")
