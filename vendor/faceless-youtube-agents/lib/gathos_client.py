import base64
import json
import time
import requests
from pathlib import Path

from lib.config import (
    GATHOS_BASE_URL,
    GATHOS_IMAGE_API_KEY,
    GATHOS_TTS_API_KEY,
    GATHOS_IMAGE_POLL_INTERVAL,
    GATHOS_TTS_POLL_INTERVAL,
    GATHOS_TIMEOUT,
    IMAGE_GEN_WIDTH,
    IMAGE_GEN_HEIGHT,
    THUMBNAIL_WIDTH,
    THUMBNAIL_HEIGHT,
)


def _image_headers():
    return {
        "Authorization": f"Bearer {GATHOS_IMAGE_API_KEY}",
        "Content-Type": "application/json",
    }


def _tts_headers():
    return {
        "Authorization": f"Bearer {GATHOS_TTS_API_KEY}",
        "Content-Type": "application/json",
    }


def submit_image_job(prompt: str, width: int = IMAGE_GEN_WIDTH, height: int = IMAGE_GEN_HEIGHT) -> str:
    for attempt in range(5):
        try:
            resp = requests.post(
                f"{GATHOS_BASE_URL}/image-generation",
                headers=_image_headers(),
                json={"prompt": prompt, "width": width, "height": height},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["job_id"]
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            if attempt < 4:
                wait = 5 * (attempt + 1)
                print(f"    Retry {attempt+1}/4 after error: {e} (waiting {wait}s)")
                time.sleep(wait)
            else:
                raise


def poll_image_job(job_id: str) -> str:
    start = time.time()
    while time.time() - start < GATHOS_TIMEOUT:
        resp = requests.get(
            f"{GATHOS_BASE_URL}/image-generation/jobs/{job_id}",
            headers=_image_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "completed":
            result = data.get("result", {})
            return result.get("image_base64", result.get("image", ""))
        if data.get("status") == "failed":
            raise RuntimeError(f"Image job {job_id} failed: {data}")
        time.sleep(GATHOS_IMAGE_POLL_INTERVAL)
    raise TimeoutError(f"Image job {job_id} timed out after {GATHOS_TIMEOUT}s")


def generate_image(prompt: str, output_path: str, width: int = IMAGE_GEN_WIDTH, height: int = IMAGE_GEN_HEIGHT) -> str:
    job_id = submit_image_job(prompt, width, height)
    print(f"  Image job submitted: {job_id}")
    b64_data = poll_image_job(job_id)
    Path(output_path).write_bytes(base64.b64decode(b64_data))
    print(f"  Image saved: {output_path}")
    return output_path


def generate_images_batch(prompts: list[dict], output_dir: str) -> list[str]:
    """Submit all image jobs first, then poll. Each dict: {prompt, filename, width?, height?}. Skips existing files."""
    jobs = []
    skipped = []
    for item in prompts:
        out_path = str(Path(output_dir) / item["filename"])
        if Path(out_path).exists() and Path(out_path).stat().st_size > 0:
            print(f"  Skipping {item['filename']} (already exists)")
            skipped.append(out_path)
            continue
        job_id = submit_image_job(
            item["prompt"],
            item.get("width", IMAGE_GEN_WIDTH),
            item.get("height", IMAGE_GEN_HEIGHT),
        )
        jobs.append({"job_id": job_id, "filename": item["filename"]})
        print(f"  Submitted image job {job_id} for {item['filename']}")

    results = list(skipped)
    for job in jobs:
        b64_data = poll_image_job(job["job_id"])
        out_path = str(Path(output_dir) / job["filename"])
        Path(out_path).write_bytes(base64.b64decode(b64_data))
        print(f"  Saved: {out_path}")
        results.append(out_path)

    return results


def submit_tts_job(text: str, voice: str) -> str:
    for attempt in range(5):
        try:
            resp = requests.post(
                f"{GATHOS_BASE_URL}/tts",
                headers=_tts_headers(),
                json={"text": text, "voice": voice},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["job_id"]
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            if attempt < 4:
                wait = 5 * (attempt + 1)
                print(f"    Retry {attempt+1}/4 after error: {e} (waiting {wait}s)")
                time.sleep(wait)
            else:
                raise


def poll_tts_job(job_id: str) -> str:
    start = time.time()
    while time.time() - start < GATHOS_TIMEOUT:
        resp = requests.get(
            f"{GATHOS_BASE_URL}/tts/jobs/{job_id}",
            headers=_tts_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "completed":
            result = data.get("result", {})
            return result.get("audio_base64", result.get("audio_wav", result.get("audio", "")))
        if data.get("status") == "failed":
            raise RuntimeError(f"TTS job {job_id} failed: {data}")
        time.sleep(GATHOS_TTS_POLL_INTERVAL)
    raise TimeoutError(f"TTS job {job_id} timed out after {GATHOS_TIMEOUT}s")


def generate_tts(text: str, voice: str, output_path: str) -> str:
    job_id = submit_tts_job(text, voice)
    print(f"  TTS job submitted: {job_id}")
    b64_data = poll_tts_job(job_id)
    Path(output_path).write_bytes(base64.b64decode(b64_data))
    print(f"  Audio saved: {output_path}")
    return output_path


def generate_tts_batch(items: list[dict], output_dir: str, voice: str) -> list[str]:
    """Submit all TTS jobs first, then poll. Each dict: {text, filename}"""
    jobs = []
    for item in items:
        job_id = submit_tts_job(item["text"], voice)
        jobs.append({"job_id": job_id, "filename": item["filename"]})
        print(f"  Submitted TTS job {job_id} for {item['filename']}")

    results = []
    for job in jobs:
        b64_data = poll_tts_job(job["job_id"])
        out_path = str(Path(output_dir) / job["filename"])
        Path(out_path).write_bytes(base64.b64decode(b64_data))
        print(f"  Saved: {out_path}")
        results.append(out_path)

    return results


def generate_thumbnail(prompt: str, output_path: str) -> str:
    return generate_image(prompt, output_path, width=THUMBNAIL_WIDTH, height=THUMBNAIL_HEIGHT)
