import json
import subprocess
import re
import tempfile
from pathlib import Path

from lib.config import YT_DLP_MAX_VIDEOS, OUTPUTS_DIR

_TMP_DIR = Path(tempfile.gettempdir())


def get_top_videos(channel_url: str, max_videos: int = YT_DLP_MAX_VIDEOS) -> list[dict]:
    """Fetch top videos from a YouTube channel sorted by view count."""
    clean_url = _normalize_channel_url(channel_url)

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        "--playlist-end", str(max_videos),
        "--extractor-args", "youtube:player_client=web",
        clean_url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")

    videos = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            videos.append({
                "id": data.get("id", ""),
                "title": data.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={data.get('id', '')}",
                "view_count": data.get("view_count", 0) or 0,
                "duration": data.get("duration", 0) or 0,
            })
        except json.JSONDecodeError:
            continue

    videos.sort(key=lambda v: v["view_count"], reverse=True)
    return videos[:max_videos]


def get_transcript(video_url: str) -> str:
    """Extract transcript from a YouTube video using yt-dlp subtitles."""
    tmp_prefix = str(_TMP_DIR / "yt_transcript_")
    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "--skip-download",
        "--output", tmp_prefix + "%(id)s.%(ext)s",
        video_url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    video_id = _extract_video_id(video_url)
    vtt_patterns = [
        _TMP_DIR / f"yt_transcript_{video_id}.en.vtt",
        _TMP_DIR / f"yt_transcript_{video_id}.en-orig.vtt",
    ]

    vtt_path = None
    for pattern in vtt_patterns:
        if pattern.exists():
            vtt_path = str(pattern)
            break

    if not vtt_path:
        from glob import glob
        matches = glob(str(_TMP_DIR / f"yt_transcript_{video_id}*.vtt"))
        if matches:
            vtt_path = matches[0]

    if not vtt_path:
        return ""

    transcript = _parse_vtt(vtt_path)
    Path(vtt_path).unlink(missing_ok=True)
    return transcript


def get_channel_transcripts(channel_url: str, max_videos: int = YT_DLP_MAX_VIDEOS) -> dict:
    """Get transcripts for top videos from a channel. Returns {video_id: {title, transcript, views}}."""
    videos = get_top_videos(channel_url, max_videos)
    print(f"Found {len(videos)} videos from channel")

    transcripts = {}
    for i, video in enumerate(videos):
        print(f"  Transcribing [{i+1}/{len(videos)}]: {video['title']}")
        transcript = get_transcript(video["url"])
        if transcript:
            transcripts[video["id"]] = {
                "title": video["title"],
                "transcript": transcript,
                "views": video["view_count"],
                "url": video["url"],
            }
            print(f"    Got {len(transcript.split())} words")
        else:
            print(f"    No transcript available, skipping")

    return transcripts


def _normalize_channel_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if "/videos" not in url and "/shorts" not in url:
        url = url + "/videos"
    return url


def _extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?/]|$)",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def _parse_vtt(vtt_path: str) -> str:
    """Parse VTT file and extract clean text without duplicates."""
    content = Path(vtt_path).read_text(encoding="utf-8", errors="ignore")

    lines = content.split("\n")
    text_lines = []
    seen = set()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r"^\d{2}:\d{2}", line) or "-->" in line:
            continue
        if re.match(r"^\d+$", line):
            continue

        clean = re.sub(r"<[^>]+>", "", line).strip()
        if not clean:
            continue

        if clean not in seen:
            seen.add(clean)
            text_lines.append(clean)

    return " ".join(text_lines)
