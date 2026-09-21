from __future__ import annotations

from dataclasses import dataclass, field

# Hard-stop states. One deliverable. No skip unless answers already stacked.
STATES = [
    "M0_intake",
    "M1_format",
    "M2_ideas",
    "M3_script",
    "M4_character",
    "M5_prompts",
    "M5b_haan",
    "M6_package_stills",
    "M7_export",
    "P0_ctr_forensic",
    "P1_titles",
    "P2_thumbs",
    "P3_listing",
    "P4_upload_draft",
]


@dataclass
class Run:
    state: str = "M0_intake"
    stacked: dict = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    def deliverable_only(self) -> str:
        return self.state

    def advance(self, haan: bool = False) -> str:
        i = STATES.index(self.state)
        nxt = STATES[min(i + 1, len(STATES) - 1)]
        if self.state == "M5b_haan" and not haan:
            raise PermissionError("M5b: HAAN required")
        if self.state == "P4_upload_draft" and not haan:
            raise PermissionError("public upload requires extra HAAN")
        self.history.append(self.state)
        self.state = nxt
        return self.state
