"""
Stage 6: Master Assembly & Dual-Aspect Broadcast Polish Engine
Pipeline — AI-Content Generation: The Heritage Short

Features:
- Seamless frame-accurate concatenation of 10 video motion clips.
- Dynamic sidechain audio ducking (-14 dB music reduction under speech).
- Broadcast-compliant Two-Pass EBU R128 Loudness Normalization (-14.0 LUFS, -1.0 dB True Peak).
- Burned-in bilingual subtitles (Amharic top line, English bottom line in mobile-safe zones).
- 7-second Heritage & AI Disclosure End Card.
- Dual broadcast exports:
    * outputs/final/film_16x9.mp4 (1920x1080, 24fps, H.264 / AAC 256k)
    * outputs/final/film_9x16.mp4 (1080x1920, 24fps, mobile-safe center-crop)
- Telemetry logging to runs.jsonl.
"""

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.utils.cache import compute_hash, is_cached, save_hash
from pipeline.utils.ffmpeg_helper import get_media_duration, run_ffmpeg
from pipeline.utils.logger import log_run

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
SHOTS_DIR = PROJECT_ROOT / "outputs" / "shots"
NARRATION_DIR = PROJECT_ROOT / "outputs" / "narration"
MUSIC_DIR = PROJECT_ROOT / "outputs" / "music"
FINAL_DIR = PROJECT_ROOT / "outputs" / "final"

TARGET_LUFS = -14.0
TARGET_TRUE_PEAK = -1.0
TARGET_LRA = 11.0


# ==============================================================================
# SUBTITLE GENERATOR (ADVANCED SUBSTATION ALPHA - .ASS)
# ==============================================================================

def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp string: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int(round((seconds - int(seconds)) * 100))
    if centis >= 100:
        centis = 99
    return f"{hrs}:{mins:02d}:{secs:02d}.{centis:02d}"


def generate_ass_subtitles(storyboard: dict) -> tuple[Path, Path]:
    """
    Generate broadcast ASS subtitles for 16:9 and 9:16 aspect ratios.
    Includes bilingual speech dialogue and final 7-second AI attribution card.
    """
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    ass_16x9_path = FINAL_DIR / "subtitles_16x9.ass"
    ass_9x16_path = FINAL_DIR / "subtitles_9x16.ass"
    
    shots = storyboard.get("shots", [])
    end_card = storyboard.get("end_card", {})
    
    # --------------------------------------------------------------------------
    # 1. 16:9 Landscape Subtitle Styles & Events
    # --------------------------------------------------------------------------
    header_16x9 = """[Script Info]
Title: The Memories of Our Home - 16:9 Broadcast Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AmharicTop,Ebrima,42,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2.8,1.5,2,80,80,95,1
Style: EnglishBottom,Ebrima,32,&H00E8E8E8,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.2,1.2,2,80,80,50,1
Style: EndCardTitle,Ebrima,54,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3.2,2.0,5,80,80,0,1
Style: EndCardTagline,Ebrima,34,&H004FD5D6,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.4,1.5,5,80,80,0,1
Style: EndCardAI,Ebrima,24,&H00C0C0C0,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.8,1.0,2,80,80,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # --------------------------------------------------------------------------
    # 2. 9:16 Vertical Subtitle Styles (Higher MarginV for mobile safe-zones)
    # --------------------------------------------------------------------------
    header_9x16 = """[Script Info]
Title: The Memories of Our Home - 9:16 Vertical Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: AmharicTop,Ebrima,40,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2.8,1.5,2,50,50,330,1
Style: EnglishBottom,Ebrima,30,&H00E8E8E8,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.2,1.2,2,50,50,285,1
Style: EndCardTitle,Ebrima,52,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3.2,2.0,5,50,50,0,1
Style: EndCardTagline,Ebrima,32,&H004FD5D6,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2.4,1.5,5,50,50,0,1
Style: EndCardAI,Ebrima,22,&H00C0C0C0,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1.8,1.0,2,50,50,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    
    # Dialogue Shots (1 to 9)
    for s in shots:
        sid = s["shot_id"]
        narration = s.get("narration", {})
        amharic = narration.get("text_amharic", "").strip()
        english = narration.get("translation_english", "").strip()
        
        if not amharic and not english:
            continue
            
        start_t = s["start_time"] + 0.35  # Natural pause before speech entry
        end_t = min(s["end_time"] - 0.20, start_t + s["duration_seconds"] - 0.20)
        
        t_start_str = format_ass_time(start_t)
        t_end_str = format_ass_time(end_t)
        
        events.append(f"Dialogue: 0,{t_start_str},{t_end_str},AmharicTop,,0,0,0,,{amharic}\n")
        events.append(f"Dialogue: 0,{t_start_str},{t_end_str},EnglishBottom,,0,0,0,,{english}\n")

    # Shot 10: Heritage End Card & AI Disclosure (83.0s to 90.0s)
    end_start = format_ass_time(83.2)
    end_end = format_ass_time(89.8)
    
    title_am = end_card.get("title_amharic", "የቤታችን ትውስታ")
    title_en = end_card.get("title_english", "The Memories of Our Home")
    tagline_am = end_card.get("tagline_amharic", "ባህላችን በእኛ ውስጥ ይኖራል።")
    tagline_en = end_card.get("tagline_english", "Our traditions live through us.")
    ai_disclosure = end_card.get("ai_disclosure_text", "Created with AI-assisted pipeline orchestration (Gemini 3.8 Flash, FLUX, Wan 2.2, ACE-Step 1.5, FFmpeg).")
    
    events.append(f"Dialogue: 0,{end_start},{end_end},EndCardTitle,,0,0,0,,{title_am}\\N{title_en}\n")
    events.append(f"Dialogue: 0,{end_start},{end_end},EndCardTagline,,0,0,0,,{tagline_am} | {tagline_en}\n")
    events.append(f"Dialogue: 0,{end_start},{end_end},EndCardAI,,0,0,0,,{ai_disclosure}\n")

    events_str = "".join(events)
    ass_16x9_path.write_text(header_16x9 + events_str, encoding="utf-8")
    ass_9x16_path.write_text(header_9x16 + events_str, encoding="utf-8")
    
    print(f"[✓] Generated Subtitles: {ass_16x9_path.name} & {ass_9x16_path.name}")
    return ass_16x9_path, ass_9x16_path


# ==============================================================================
# AUDIO DUCKING & TWO-PASS EBU R128 NORMALIZATION
# ==============================================================================

def master_audio_track(storyboard: dict) -> Path:
    """
    Produce the broadcast master audio track:
    1. Align narration stems with exact millisecond delay.
    2. Sidechain-compress music under dialogue (-14 dB attenuation).
    3. Pass 1: Measure integrated loudness and True Peak.
    4. Pass 2: Apply exact EBU R128 normalization to -14.0 LUFS / -1.0 dB True Peak.
    """
    shots = storyboard.get("shots", [])
    selected_music = MUSIC_DIR / "selected_score.wav"
    raw_mixed_path = FINAL_DIR / "raw_mix.wav"
    master_audio_path = FINAL_DIR / "master_audio.wav"
    
    print("\n--- Audio Mastering: Sidechain Ducking & EBU R128 Loudness ---")
    
    # 1. Build FFmpeg command to assemble raw mix
    cmd = ["-y", "-i", str(selected_music)]
    narration_inputs = []
    filter_complex = []
    
    for idx, s in enumerate(shots):
        sid = s["shot_id"]
        stem = NARRATION_DIR / f"{sid}.wav"
        start_ms = int(s["start_time"] * 1000)
        
        if stem.exists() and stem.stat().st_size > 1000:
            cmd.extend(["-i", str(stem)])
            in_idx = 1 + len(narration_inputs)
            narration_inputs.append(in_idx)
            filter_complex.append(f"[{in_idx}:a]adelay={start_ms}|{start_ms}[delayed_{idx}];")
            
    # Combine narration stems
    voice_pads = "".join([f"[delayed_{i}]" for i in range(len(narration_inputs))])
    filter_complex.append(f"{voice_pads}amix=inputs={len(narration_inputs)}:dropout_transition=0:normalize=0[voice_raw];")
    filter_complex.append("[voice_raw]asplit=2[voice_sc][voice_mix];")
    
    # Sidechain compress music under speech (-14 dB attenuation with smooth 150ms attack, 900ms release)
    filter_complex.append(
        "[0:a]volume=0.85[music_base];"
        "[music_base][voice_sc]sidechaincompress=threshold=0.025:ratio=5.0:attack=150:release=900[ducked_music];"
        "[ducked_music][voice_mix]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[raw_audio]"
    )
    
    cmd.extend([
        "-filter_complex", "".join(filter_complex),
        "-map", "[raw_audio]",
        "-c:a", "pcm_s16le",
        "-ar", "48000",
        "-t", "90.0",
        str(raw_mixed_path)
    ])
    
    res = run_ffmpeg(cmd, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Audio mixing failed: {res.stderr[-600:]}")
        
    # 2. Pass 1: Measure loudness with loudnorm filter
    print("  [Pass 1] Measuring integrated loudness & True Peak ...")
    measure_cmd = [
        "-i", str(raw_mixed_path),
        "-af", f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}:print_format=json",
        "-f", "null", "-"
    ]
    measure_res = run_ffmpeg(measure_cmd, check=False)
    
    # Parse JSON output from stderr
    stderr_text = measure_res.stderr
    json_match = re.search(r"\{[\s\S]*?\"input_i\"[\s\S]*?\}", stderr_text)
    if not json_match:
        print("  [WARN] Loudnorm JSON stats not found, using single-pass normalization.")
        norm_filter = f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}"
    else:
        stats = json.loads(json_match.group(0))
        input_i = stats.get("input_i", "-16.0")
        input_tp = stats.get("input_tp", "-1.5")
        input_lra = stats.get("input_lra", "11.0")
        input_thresh = stats.get("input_thresh", "-26.0")
        target_offset = stats.get("target_offset", "0.0")
        
        print(f"  [Pass 1 Stats] Measured I: {input_i} LUFS | TP: {input_tp} dBTP | LRA: {input_lra} LU")
        norm_filter = (
            f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TRUE_PEAK}:LRA={TARGET_LRA}:"
            f"measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
            f"measured_thresh={input_thresh}:offset={target_offset}:linear=true"
        )
        
    # 3. Pass 2: Normalize to target broadcast master
    print(f"  [Pass 2] Normalizing to strict target: {TARGET_LUFS} LUFS, {TARGET_TRUE_PEAK} dBTP ...")
    norm_cmd = [
        "-y",
        "-i", str(raw_mixed_path),
        "-af", norm_filter,
        "-c:a", "pcm_s16le",
        "-ar", "48000",
        str(master_audio_path)
    ]
    norm_res = run_ffmpeg(norm_cmd, check=False)
    if norm_res.returncode != 0:
        raise RuntimeError(f"Loudness normalization pass failed: {norm_res.stderr[-600:]}")
        
    print(f"  [✓] Master Audio Complete: {master_audio_path.name}")
    return master_audio_path


# ==============================================================================
# DUAL ASPECT RATIO COMPOSITOR (16:9 & 9:16)
# ==============================================================================

def assemble_final_film(aspect_ratio: str = "16:9", force: bool = False) -> Path:
    """
    Composite final film in specified aspect ratio (16:9 or 9:16).
    """
    t0 = time.time()
    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
        
    shots = storyboard.get("shots", [])
    is_vertical = (aspect_ratio == "9:16")
    
    out_filename = "film_9x16.mp4" if is_vertical else "film_16x9.mp4"
    output_path = FINAL_DIR / out_filename
    
    cache_payload = {
        "aspect_ratio": aspect_ratio,
        "target_duration": storyboard.get("total_duration_seconds", 90.0),
        "resolution": "1080x1920" if is_vertical else "1920x1080",
        "shots_count": len(shots)
    }
    
    if not force and is_cached(output_path, cache_payload):
        print(f"\n[⚡ CACHED] {out_filename} already generated and valid.")
        return output_path
        
    print(f"\n==================================================")
    print(f"COMPOSITING FINAL FILM: {aspect_ratio.upper()} ({out_filename})")
    print(f"Resolution: {'1080x1920 (Vertical Mobile)' if is_vertical else '1920x1080 (Landscape Broadcast)'}")
    print(f"Duration: 90.00s | Codec: H.264 (CRF 18) | Audio: AAC 256k")
    print("==================================================")
    
    # 1. Subtitles
    ass_16x9, ass_9x16 = generate_ass_subtitles(storyboard)
    sub_path = ass_9x16 if is_vertical else ass_16x9
    # Use relative forward-slash path to avoid Windows drive colon escaping issues in FFmpeg filter syntax
    sub_arg = f"outputs/final/{sub_path.name}"
    
    # 2. Master Audio (rebuild if missing, forced, or any narration/music input is newer)
    master_audio = FINAL_DIR / "master_audio.wav"
    input_stems = [MUSIC_DIR / "selected_score.wav"] + [
        NARRATION_DIR / f"{s['shot_id']}.wav" for s in shots
    ]
    newest_input_mtime = max(
        (p.stat().st_mtime for p in input_stems if p.exists()),
        default=0.0,
    )
    audio_stale = (not master_audio.exists()) or (
        newest_input_mtime > master_audio.stat().st_mtime
    )
    if force or audio_stale:
        master_audio = master_audio_track(storyboard)
        
    # 3. Video Concat list
    concat_list_path = FINAL_DIR / "concat_shots.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for s in shots:
            sid = s["shot_id"]
            p = (SHOTS_DIR / f"{sid}.mp4").resolve()
            f.write(f"file '{p.as_posix()}'\n")
            
    # 4. Construct Video Filtergraph
    if is_vertical:
        # Scale to fit 1920 height, center crop to 1080 width (Mobile 9:16), then burn subtitles
        vf = f"scale=3413:1920,crop=1080:1920:(iw-1080)/2:0,ass={sub_arg}"
    else:
        # Native 1920x1080 landscape, burn subtitles
        vf = f"ass={sub_arg}"
        
    cmd = [
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-i", str(master_audio),
        "-vf", vf,
        "-map", "0:v",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "48000",
        "-t", "90.0",
        str(output_path)
    ]
    
    res = run_ffmpeg(cmd, check=False)
    if res.returncode != 0:
        raise RuntimeError(f"Final film assembly failed: {res.stderr[-800:]}")
        
    dur = get_media_duration(output_path)
    latency = round(time.time() - t0, 2)
    size_mb = round(output_path.stat().st_size / (1024 * 1024), 2)
    save_hash(output_path, cache_payload)
    
    print(f"\n[✓] SUCCESS: {out_filename} Exported!")
    print(f"    Size: {size_mb} MB | Duration: {dur:.2f}s | Wall-clock: {latency}s")
    
    log_run(
        stage="06_assemble",
        target=out_filename,
        model="ffmpeg_master_compositor",
        parameters={"aspect_ratio": aspect_ratio, "duration": dur, "crf": 18},
        latency_seconds=latency,
        status="success",
        metadata={
            "aspect_ratio": aspect_ratio,
            "resolution": "1080x1920" if is_vertical else "1920x1080",
            "file_size_mb": size_mb,
            "duration_seconds": dur
        }
    )
    
    return output_path


def verify_master_deliverables() -> bool:
    """
    Validate both exported films against the contract and broadcast specifications.
    """
    print("\n==================================================")
    print("MASTER DELIVERABLES VERIFICATION REPORT")
    print("==================================================")
    
    film_16x9 = FINAL_DIR / "film_16x9.mp4"
    film_9x16 = FINAL_DIR / "film_9x16.mp4"
    
    all_ok = True
    for p, expected_ar in [(film_16x9, "16:9"), (film_9x16, "9:16")]:
        if not p.exists():
            print(f"  [FAIL] Deliverable missing: {p.name}")
            all_ok = False
            continue
            
        dur = get_media_duration(p)
        size_mb = round(p.stat().st_size / (1024 * 1024), 2)
        dur_ok = abs(dur - 90.0) <= 0.1
        
        status = "PASS ✅" if dur_ok else "FAIL ❌"
        print(f"  {p.name:<16} | AR: {expected_ar:<5} | Size: {size_mb:5.2f} MB | Duration: {dur:5.2f}s | {status}")
        if not dur_ok:
            all_ok = False
            
    # Measure integrated loudness of final film
    if film_16x9.exists():
        check_cmd = [
            "-i", str(film_16x9),
            "-af", "ebur128=framelog=verbose",
            "-f", "null", "-"
        ]
        res = run_ffmpeg(check_cmd, check=False)
        match = re.search(r"Integrated loudness:\s+I:\s+([-\d.]+)\s+LUFS", res.stderr)
        if match:
            measured_lufs = float(match.group(1))
            lufs_ok = abs(measured_lufs - TARGET_LUFS) <= 1.0
            print(f"  Broadcast Loudness: {measured_lufs:.1f} LUFS (Target: {TARGET_LUFS} LUFS) -> {'COMPLIANT ✅' if lufs_ok else 'OUT OF SPEC ❌'}")
            
    print("==================================================")
    return all_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 6: Master Assembly & Dual-Aspect Polish")
    parser.add_argument("--aspect", choices=["16:9", "9:16", "all"], default="all", help="Target aspect ratio")
    parser.add_argument("--force", action="store_true", help="Force re-rendering without cache")
    args = parser.parse_args()
    
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    
    if args.aspect in ["16:9", "all"]:
        assemble_final_film("16:9", force=args.force)
        
    if args.aspect in ["9:16", "all"]:
        assemble_final_film("9:16", force=args.force)
        
    verify_master_deliverables()
