"""
Phase 2 Checkpoint: Rough Cut Assembler
Assembles all 10 video motion shots, timed Amharic narration, and the auditioned
original Ethiopian acoustic score into a complete, watchable rough cut film.

Outputs: outputs/rough_cut/rough_cut.mp4 (90.00s, 1920x1080 @ 24fps)
"""

import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.utils.ffmpeg_helper import get_media_duration, run_ffmpeg
from pipeline.utils.logger import log_run

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
SHOTS_DIR = PROJECT_ROOT / "outputs" / "shots"
NARRATION_DIR = PROJECT_ROOT / "outputs" / "narration"
MUSIC_DIR = PROJECT_ROOT / "outputs" / "music"
ROUGH_CUT_DIR = PROJECT_ROOT / "outputs" / "rough_cut"
OUTPUT_FILE = ROUGH_CUT_DIR / "rough_cut.mp4"


def assemble_rough_cut():
    start_time = time.time()
    ROUGH_CUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(STORYBOARD_PATH, "r", encoding="utf-8") as f:
        storyboard = json.load(f)
        
    shots = storyboard.get("shots", [])
    selected_music = MUSIC_DIR / "selected_score.wav"
    
    if not selected_music.exists():
        raise FileNotFoundError(f"Selected score not found: {selected_music}. Run pipeline/05_music.py first.")
        
    # Check that all 10 video shots exist
    for s in shots:
        sid = s["shot_id"]
        shot_path = SHOTS_DIR / f"{sid}.mp4"
        if not shot_path.exists():
            raise FileNotFoundError(f"Shot video missing: {shot_path}. Run pipeline/04_shots.py first.")
            
    print("==================================================")
    print("PHASE 2 CHECKPOINT: ASSEMBLING ROUGH CUT")
    print(f"Targeting: 10 Video Shots + Amharic Voice + Original Score")
    print(f"Output: {OUTPUT_FILE}")
    print("==================================================")
    
    # 1. Create temporary concat list for video shots
    concat_list_path = ROUGH_CUT_DIR / "concat_shots.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for s in shots:
            sid = s["shot_id"]
            p = (SHOTS_DIR / f"{sid}.mp4").resolve()
            f.write(f"file '{p.as_posix()}'\n")
            
    # 2. Build multi-track audio mix using FFmpeg
    # Input 0: Concat video shots
    # Input 1: Music track (selected_score.wav)
    # Inputs 2..N: Narration stems delayed by shot start_time
    ffmpeg_cmd = [
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_path),
        "-i", str(selected_music)
    ]
    
    narration_inputs = []
    filter_complex = []
    
    for idx, s in enumerate(shots):
        sid = s["shot_id"]
        audio_stem = NARRATION_DIR / f"{sid}.wav"
        start_ms = int(s["start_time"] * 1000)
        
        if audio_stem.exists() and audio_stem.stat().st_size > 1000:
            ffmpeg_cmd.extend(["-i", str(audio_stem)])
            input_idx = 2 + len(narration_inputs)
            narration_inputs.append(input_idx)
            # Add adelay to position voice accurately
            filter_complex.append(f"[{input_idx}:a]adelay={start_ms}|{start_ms}[delayed_{idx}];")
            
    # Mix all narration stems
    voice_pads = "".join([f"[delayed_{i}]" for i in range(len(narration_inputs))])
    filter_complex.append(f"{voice_pads}amix=inputs={len(narration_inputs)}:dropout_transition=0:normalize=0[voice_raw];")
    
    # Split voice pad: one for sidechain ducking detector, one for final audio mix
    filter_complex.append("[voice_raw]asplit=2[voice_sc][voice_mix];")
    
    # Sidechain compress music under voice
    filter_complex.append(
        "[1:a]volume=0.85[music_base];"
        "[music_base][voice_sc]sidechaincompress=threshold=0.03:ratio=4.5:attack=150:release=900[ducked_music];"
        "[ducked_music][voice_mix]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mixed_audio]"
    )
    
    full_filter = "".join(filter_complex)
    
    ffmpeg_cmd.extend([
        "-filter_complex", full_filter,
        "-map", "0:v",
        "-map", "[mixed_audio]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "90.0",
        str(OUTPUT_FILE)
    ])
    
    res = run_ffmpeg(ffmpeg_cmd, check=False)
    if res.returncode != 0:
        print("[FAIL] FFmpeg rough cut assembly error:")
        print(res.stderr[-1000:])
        return False
        
    dur = get_media_duration(OUTPUT_FILE)
    latency = round(time.time() - start_time, 2)
    size_mb = round(OUTPUT_FILE.stat().st_size / (1024 * 1024), 2)
    
    print(f"\n[✓] SUCCESS: Rough Cut Rendered!")
    print(f"    File: {OUTPUT_FILE} ({size_mb} MB)")
    print(f"    Duration: {dur:.2f}s (Target: 90.0s)")
    print(f"    Wall-clock Latency: {latency}s")
    
    log_run(
        stage="phase2_rough_cut",
        target="rough_cut.mp4",
        model="ffmpeg_rough_cut_compositor",
        parameters={"duration": dur, "shots": len(shots)},
        latency_seconds=latency,
        status="success",
        metadata={"file_size_mb": size_mb, "duration_seconds": dur}
    )
    
    return True


if __name__ == "__main__":
    assemble_rough_cut()
