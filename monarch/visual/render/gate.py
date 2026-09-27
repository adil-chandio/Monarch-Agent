from monarch.core.haan import require_haan


def render_full_video(operator_said: str) -> str:
    require_haan(operator_said, "render")
    return (
        "HAAN accepted. Generate media in Arena Agent Mode "
        "(images + speech) from locked prompts. No local ffmpeg/Flow."
    )
