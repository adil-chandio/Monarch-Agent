from __future__ import annotations

from dataclasses import dataclass, field

STATES = [
<<<<<<< HEAD
=======
    "I0_intake",
>>>>>>> b1e1ed3 (Activate asks 4 questions first; 2-3s cuts; present mp4; VO recommend.)
    "F0_forensic_hunt",
    "M2_ideas_plus_top1",
    "F1_script_forensic",
    "M3_script",
    "M4_character",
    "M5_boards",
    "M5b_haan_video",
    "M5c_video_qc",
    "M6_thumbs",
    "P3_listing",
    "DONE_human_upload",
]

WAIT_FOR = {
<<<<<<< HEAD
=======
    "I0_intake": "channel/niche + ratio + short/long + language",
>>>>>>> b1e1ed3 (Activate asks 4 questions first; 2-3s cuts; present mp4; VO recommend.)
    "M2_ideas_plus_top1": "pick number or haan on TOP 1",
    "M3_script": "perfect | improve",
    "M5b_haan_video": "haan",
    "M5c_video_qc": "perfect | reedit",
    "M6_thumbs": "approve | redo",
    "P3_listing": "approve metadata",
}


@dataclass
class Run:
<<<<<<< HEAD
    state: str = "F0_forensic_hunt"
=======
    state: str = "I0_intake"
>>>>>>> b1e1ed3 (Activate asks 4 questions first; 2-3s cuts; present mp4; VO recommend.)
    stacked: dict = field(default_factory=dict)
    history: list[str] = field(default_factory=list)

    def wait_prompt(self) -> str | None:
        return WAIT_FOR.get(self.state)

    def advance(self, token: str = "") -> str:
        t = (token or "").strip().lower()
        need = WAIT_FOR.get(self.state)
        if need:
            ok = False
            if self.state == "M2_ideas_plus_top1":
                ok = t.isdigit() or t in {"haan", "han", "yes", "1"}
            elif self.state == "M3_script":
                ok = t in {"perfect", "improve", "haan"}
            elif self.state == "M5b_haan_video":
                ok = t in {"haan", "han", "yes"}
            elif self.state == "M5c_video_qc":
                ok = t in {"perfect", "reedit", "re-edit", "haan"}
            elif self.state in {"M6_thumbs", "P3_listing"}:
                ok = t in {"approve", "redo", "haan", "perfect"}
            if not ok:
                raise PermissionError(f"STOP. WAIT: {need}")
        i = STATES.index(self.state)
        self.history.append(self.state)
        if self.state == "M3_script" and t == "improve":
            return self.state
        if self.state == "M5c_video_qc" and t in {"reedit", "re-edit"}:
            self.state = "M5b_haan_video"
            return self.state
        if self.state == "M6_thumbs" and t == "redo":
            return self.state
        self.state = STATES[min(i + 1, len(STATES) - 1)]
        return self.state
