from __future__ import annotations

from monarch.core.haan import require_haan


def upload_draft(operator: str, listing: dict) -> dict:
    require_haan(operator, "upload_draft")
    if listing.get("privacy") == "public":
        raise PermissionError("public requires a second HAAN")
    return {"status": "queued_draft_local_only", "listing": listing}
