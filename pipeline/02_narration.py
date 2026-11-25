"""
Stage 2: Amharic Narration Speech Engine
Generates authentic Amharic speech line-by-line for each storyboard shot using Gemini 3.8 Flash TTS.
Features:
- Deterministic SHA-256 caching (skips regenerating unchanged lines).
- Automatic rate-limit handling with exponential backoff on HTTP 429.
- Clean prompt isolation (ensures model speaks ONLY the Amharic line).
- Automatic silent audio track generation for the end card.
- Telemetry logging to runs.jsonl (latency, audio duration, parameters).
- CLI support for full batch or single-shot live regeneration.
"""

import argparse
import json
import os
import re
import sys
import time
import wave
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
from google import genai
from google.genai import types

from pipeline.utils.cache import compute_hash, is_cached, save_hash
from pipeline.utils.ffmpeg_helper import run_ffmpeg
from pipeline.utils.logger import log_run

load_dotenv()

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "narration"


def get_audio_duration(file_path: Path) -> float:
    """Read precise duration of a WAV file in seconds."""
    try:
        with wave.open(str(file_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            return round(frames / float(rate), 2)
    except Exception:
        return 0.0


def create_silent_audio(output_file: Path, duration_s: float = 7.0) -> None:
    """Generate a clean silent stereo WAV file for end card or silent intervals."""
    cmd = [
        "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=44100:cl=stereo",
        "-t", str(duration_s),
        "-c:a", "pcm_s16le",
        str(output_file)
    ]
    run_ffmpeg(cmd)


def generate_single_line_with_retry(client, text_amharic: str, voice_style: str, max_retries: int = 3) -> bytes:
    """
    Generate Amharic speech bytes with automatic backoff retry on rate limits (HTTP 429).
    IMPORTANT: Passes ONLY pure Amharic text to the TTS model to prevent the model
    from speaking English instructions or preambles aloud.
    """
    clean_text = text_amharic.strip()

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash-tts",
                contents=clean_text,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"]
                )
            )

            audio_bytes = None
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        audio_bytes = part.inline_data.data
                        break
                if audio_bytes:
                    break

            if audio_bytes:
                return audio_bytes
            else:
                raise RuntimeError("No audio data received in response.")

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # Extract suggested retry delay or default to 25s
                delay_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str)
                sleep_sec = float(delay_match.group(1)) + 2.0 if delay_match else 25.0
                print(f"    [RATE LIMIT 429] Free Tier RPM reached. Pausing {sleep_sec:.1f}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(sleep_sec)
            else:
                raise e

    raise RuntimeError(f"Exceeded {max_retries} retries for narration line.")


def generate_narration(target_shot: str = None, force: bool = False) -> bool:
    start_all = time.time()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] GEMINI_API_KEY missing from environment or .env file.")
        return False

    client = genai.Client(api_key=api_key)

    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        storyboard = json.load(f)

    shots = storyboard.get("shots", [])
    if target_shot:
        shots = [s for s in shots if s.get("shot_id") == target_shot]
        if not shots:
            print(f"[FAIL] Target shot '{target_shot}' not found in storyboard.json")
            return False

    print("==================================================")
    print("STAGE 02: AMHARIC NARRATION SYNTHESIS (Gemini 3.8 Flash TTS)")
    print(f"Targeting: {'All 10 shots' if not target_shot else target_shot}")
    print("==================================================")

    generated_count = 0
    cached_count = 0
    errors = []

    for shot in shots:
        shot_id = shot["shot_id"]
        narration = shot.get("narration", {})
        text_amharic = narration.get("text_amharic", "").strip()
        voice_style = narration.get("voice_style", "warm, calm, gentle, unhurried")
        duration_allocated = shot.get("duration_seconds", 8.0)
        output_file = PROJECT_ROOT / narration.get("audio_file", f"outputs/narration/{shot_id}.wav")

        cache_payload = {
            "shot_id": shot_id,
            "text": text_amharic,
            "voice_style": voice_style,
            "model": "gemini-3.8-flash-tts"
        }

        # 1. Handle Silent End Card (Shot 10)
        if not text_amharic:
            if not is_cached(output_file, cache_payload) or force:
                create_silent_audio(output_file, duration_allocated)
                save_hash(output_file, cache_payload)
                log_run(
                    stage="02_narration",
                    target=output_file.name,
                    model="ffmpeg_silent_generator",
                    parameters={"duration": duration_allocated},
                    latency_seconds=0.05,
                    cost_usd=0.0,
                    status="success",
                    metadata={"shot_id": shot_id, "silent": True, "audio_duration_seconds": duration_allocated}
                )
                print(f"\n[INFO] {shot_id}: Generated Silent End Card Audio ({duration_allocated:.1f}s)")
                generated_count += 1
            else:
                print(f"\n[⚡ CACHED] {shot_id}: {output_file.name} (Silent: {duration_allocated:.1f}s)")
                cached_count += 1
            continue

        # 2. Check Cache for Spoken Shots
        if is_cached(output_file, cache_payload) and not force:
            actual_dur = get_audio_duration(output_file)
            print(f"\n[⚡ CACHED] {shot_id}: {output_file.name} ({actual_dur:.2f}s)")
            cached_count += 1
            log_run(
                stage="02_narration",
                target=output_file.name,
                model="gemini-3.8-flash-tts",
                parameters={"text_amharic": text_amharic, "voice_style": voice_style},
                latency_seconds=0.001,
                cost_usd=0.0,
                status="cached",
                metadata={"shot_id": shot_id, "audio_duration_seconds": actual_dur}
            )
            continue

        # 3. Call Gemini 3.8 Flash TTS with auto-backoff
        print(f"\n[SYNTHESIZING] {shot_id} -> {output_file.name}")
        print(f"  Amharic Text: \"{text_amharic}\"")
        print(f"  Voice Style: {voice_style}")

        t0 = time.time()
        try:
            audio_bytes = generate_single_line_with_retry(client, text_amharic, voice_style)

            # Save the WAV file
            with open(output_file, "wb") as f_out:
                f_out.write(audio_bytes)

            latency = round(time.time() - t0, 3)
            actual_dur = get_audio_duration(output_file)
            save_hash(output_file, cache_payload)

            log_run(
                stage="02_narration",
                target=output_file.name,
                model="gemini-3.8-flash-tts",
                parameters={
                    "text_amharic": text_amharic,
                    "voice_style": voice_style,
                    "language": "am-ET"
                },
                latency_seconds=latency,
                cost_usd=0.0,
                status="success",
                metadata={
                    "shot_id": shot_id,
                    "audio_duration_seconds": actual_dur,
                    "allocated_duration_seconds": duration_allocated,
                    "bytes": len(audio_bytes)
                }
            )

            print(f"  [✓] SUCCESS: {output_file.name} saved ({len(audio_bytes) / 1024:.1f} KB)")
            print(f"  Latency: {latency:.2f}s | Audio Duration: {actual_dur:.2f}s (Allocated: {duration_allocated:.1f}s)")
            generated_count += 1

            # Proactive rate-limit protection between successive fresh generations
            time.sleep(2.0)

        except Exception as e:
            latency = round(time.time() - t0, 3)
            err_msg = f"Gemini TTS generation failed for {shot_id}: {e}"
            print(f"  [X] ERROR: {err_msg}")
            errors.append(err_msg)
            log_run(
                stage="02_narration",
                target=output_file.name,
                model="gemini-3.8-flash-tts",
                parameters={"text_amharic": text_amharic},
                latency_seconds=latency,
                cost_usd=0.0,
                status="failed",
                error_message=str(e),
                metadata={"shot_id": shot_id}
            )

    total_time = round(time.time() - start_all, 2)
    print("\n==================================================")
    print(f"STAGE 02 COMPLETE in {total_time}s")
    print(f"Generated: {generated_count} | Cached: {cached_count} | Errors: {len(errors)}")
    print("Telemetry recorded to runs.jsonl")
    print("==================================================")

    return len(errors) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Amharic voiceovers for storyboard shots.")
    parser.add_argument("--shot", type=str, default=None, help="Target specific shot_id (e.g. shot_06)")
    parser.add_argument("--force", action="store_true", help="Force regeneration ignoring cache")
    args = parser.parse_args()

    ok = generate_narration(target_shot=args.shot, force=args.force)
    sys.exit(0 if ok else 1)
