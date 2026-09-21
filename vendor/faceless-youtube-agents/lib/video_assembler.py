import json
import subprocess
from pathlib import Path

from lib.config import (
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    DISSOLVE_DURATION,
    FPS,
)


def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def create_slide_clip(image_path: str, audio_path: str, output_path: str) -> str:
    """Create a single clip from an image + audio with Ken Burns slow zoom effect."""
    audio_dur = get_audio_duration(audio_path)
    total_frames = int(audio_dur * FPS)

    # Ken Burns: slow zoom from 1.0x to 1.12x, centered
    # zoompan needs a larger input so we scale up first, then zoompan crops
    zoom_speed = 0.12 / total_frames if total_frames > 0 else 0.0005
    vf = (
        f"scale=8000:-1,"
        f"zoompan=z='1+{zoom_speed:.8f}*in':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={total_frames}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={FPS}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg clip failed: {result.stderr}")
    return output_path


def concatenate_clips(clip_paths: list[str], output_path: str) -> str:
    """Concatenate multiple clips into one video using concat demuxer."""
    filelist_path = str(Path(output_path).parent / "_concat_list.txt")
    with open(filelist_path, "w") as f:
        for clip in clip_paths:
            f.write(f"file '{clip}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", filelist_path,
        "-c", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed: {result.stderr}")

    Path(filelist_path).unlink(missing_ok=True)
    return output_path


def create_slideshow_with_dissolves(
    image_paths: list[str],
    durations: list[float],
    output_path: str,
) -> str:
    """Create a slideshow from images with dissolve transitions between them."""
    if len(image_paths) == 1:
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(durations[0]),
            "-i", image_paths[0],
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg slideshow failed: {result.stderr}")
        return output_path

    inputs = []
    filter_parts = []
    for i, (img, dur) in enumerate(zip(image_paths, durations)):
        inputs.extend(["-loop", "1", "-t", str(dur + DISSOLVE_DURATION), "-i", img])
        filter_parts.append(
            f"[{i}:v]scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps={FPS}[v{i}]"
        )

    xfade_chain = "[v0]"
    offset = durations[0]
    for i in range(1, len(image_paths)):
        out_label = f"[xf{i}]" if i < len(image_paths) - 1 else "[outv]"
        filter_parts.append(
            f"{xfade_chain}[v{i}]xfade=transition=fade:duration={DISSOLVE_DURATION}:offset={offset:.2f}{out_label}"
        )
        xfade_chain = out_label
        offset += durations[i] - DISSOLVE_DURATION

    filter_complex = ";".join(filter_parts)

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg dissolve failed: {result.stderr}")
    return output_path


def assemble_video(run_dir: str, slides_json: dict) -> str:
    """Full assembly: for each slide, create image+audio clip, then concatenate all."""
    run_path = Path(run_dir)
    clips_dir = run_path / "clips"
    clips_dir.mkdir(exist_ok=True)

    slides = slides_json["slides"]
    clip_paths = []

    for slide in slides:
        num = slide["slide_number"]
        img_path = str(run_path / "slides" / f"slide-{num:02d}.png")
        audio_path = str(run_path / "audio" / f"slide-{num:02d}.wav")
        clip_path = str(clips_dir / f"clip-{num:02d}.mp4")

        if not Path(img_path).exists():
            raise FileNotFoundError(f"Missing image: {img_path}")
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Missing audio: {audio_path}")

        print(f"  Creating clip {num}: {img_path} + {audio_path}")
        create_slide_clip(img_path, audio_path, clip_path)
        clip_paths.append(clip_path)

    final_path = str(run_path / "final.mp4")
    print(f"  Concatenating {len(clip_paths)} clips...")
    concatenate_clips(clip_paths, final_path)

    for clip in clip_paths:
        Path(clip).unlink(missing_ok=True)
    clips_dir.rmdir()

    print(f"  Final video: {final_path}")
    return final_path
