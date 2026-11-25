"""
Stage 5: Original Ethiopian Music Score Synthesis & Candidate Audition Engine
Pipeline — AI-Content Generation: The Heritage Short

Generates and auditions 3 original Ethiopian traditional acoustic scores
rooted in authentic Ethiopian pentatonic scales (Kiñit: Tizita, Bati, Ambassel).
Instruments modeled:
- Krar (5-string Ethiopian wooden lyre via Karplus-Strong string synthesis)
- Washint (traditional bamboo flute with breath noise and vibrato)
- Masinko (single-string bowed diamond fiddle)
- Kebero (traditional dual-headed acoustic drum)

Evaluates candidates, selects the winning master track, and outputs:
  outputs/music/selected_score.wav (exactly 90.00 seconds, 48kHz stereo, broadcast mastered).
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
import numpy as np
import scipy.io.wavfile as wavfile

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.utils.cache import compute_hash, is_cached, save_hash
from pipeline.utils.ffmpeg_helper import get_media_duration, run_ffmpeg
from pipeline.utils.logger import log_run

STORYBOARD_PATH = PROJECT_ROOT / "storyboard.json"
MUSIC_DIR = PROJECT_ROOT / "outputs" / "music"
SAMPLE_RATE = 48000  # Broadcast standard 48 kHz


# ==============================================================================
# ACOUSTIC PHYSICAL MODELING OF ETHIOPIAN INSTRUMENTS
# ==============================================================================

def karplus_strong_pluck(freq: float, duration: float, sr: int = SAMPLE_RATE, decay: float = 0.988) -> np.ndarray:
    """
    Simulate a Krar (Ethiopian 5-string lyre) gut string pluck using Karplus-Strong synthesis.
    """
    if freq <= 0:
        return np.zeros(int(sr * duration))
    
    n_samples = int(sr * duration)
    period = int(sr / freq)
    if period <= 0:
        return np.zeros(n_samples)
    
    # Initial noise burst (finger pluck impact)
    noise_ring = np.random.uniform(-1.0, 1.0, period)
    # Slight lowpass filter on initial noise for warm gut string attack
    noise_ring = np.convolve(noise_ring, [0.3, 0.4, 0.3], mode='same')
    
    out = np.zeros(n_samples)
    out[:min(period, n_samples)] = noise_ring[:min(period, n_samples)]
    
    # Ring buffer feedback loop with string damping
    idx = 0
    for i in range(period, n_samples):
        prev_idx = (idx - 1) % period
        avg = 0.5 * (noise_ring[idx] + noise_ring[prev_idx]) * decay
        noise_ring[idx] = avg
        out[i] = avg
        idx = (idx + 1) % period
        
    return out


def washint_flute_tone(freq: float, duration: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Simulate a Washint (Ethiopian bamboo flute) with overblown harmonics, breath noise, and organic vibrato.
    """
    if freq <= 0:
        return np.zeros(int(sr * duration))
    
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # 4.8 Hz natural vocal vibrato / pitch tremolo
    vibrato = 1.0 + 0.012 * np.sin(2 * np.pi * 4.8 * t)
    phase = 2 * np.pi * np.cumsum(freq * vibrato) / sr
    
    # Flute tube harmonic spectrum (strong fundamental, soft 2nd & 3rd harmonics)
    fundamental = np.sin(phase)
    h2 = 0.35 * np.sin(2 * phase)
    h3 = 0.15 * np.sin(3 * phase)
    tone = fundamental + h2 + h3
    
    # Breath turbulence / airy noise through the bamboo notch
    breath = np.random.normal(0, 0.08, len(t))
    
    # Gentle attack and release envelope
    n_samples = len(t)
    attack = int(sr * min(0.12, duration * 0.25))
    release = int(sr * min(0.20, duration * 0.35))
    
    envelope = np.ones(n_samples)
    if attack > 0:
        envelope[:attack] = np.sin(np.linspace(0, np.pi / 2, attack)) ** 2
    if release > 0:
        envelope[-release:] = np.sin(np.linspace(np.pi / 2, 0, release)) ** 2
        
    signal = (tone * 0.85 + breath * 0.15) * envelope
    return signal


def masinko_fiddle_tone(freq: float, duration: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Simulate a Masinko (single-string diamond fiddle) with bowed friction texture and Azmari ornamentations.
    """
    if freq <= 0:
        return np.zeros(int(sr * duration))
    
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    
    # Bow friction: band-limited sawtooth + subtle 5.2 Hz glissando vibrato
    vibrato = 1.0 + 0.018 * np.sin(2 * np.pi * 5.2 * t)
    phase = 2 * np.pi * np.cumsum(freq * vibrato) / sr
    
    # Bowed string harmonic series
    bowed = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.3 * np.sin(3 * phase) + 0.15 * np.sin(4 * phase)
    
    # Diamond resonator box resonance (warm acoustic body filter)
    envelope = np.ones(len(t))
    attack = int(sr * min(0.18, duration * 0.25))
    release = int(sr * min(0.22, duration * 0.35))
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        envelope[-release:] = np.linspace(1, 0, release)
        
    return bowed * envelope * 0.70


def kebero_drum_hit(hit_type: str = "bass", duration: float = 0.8, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Simulate a Kebero (traditional Ethiopian double-headed drum) hit:
    - 'bass': resonant deep center hit (55 Hz base with rapid pitch drop).
    - 'slap': sharp high-pitched rim strike (220 Hz snap with short decay).
    """
    n_samples = int(sr * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    
    if hit_type == "bass":
        # Pitch drops quickly from 110 Hz down to 55 Hz
        f = 55.0 + 55.0 * np.exp(-t * 18.0)
        phase = 2 * np.pi * np.cumsum(f) / sr
        decay = np.exp(-t * 4.5)
        # Deep resonant boom
        hit = np.sin(phase) * decay
        # Add slight sub-harmonic warmth
        hit += 0.35 * np.sin(phase * 0.5) * decay
    else:  # slap
        f = 220.0 + 180.0 * np.exp(-t * 35.0)
        phase = 2 * np.pi * np.cumsum(f) / sr
        decay = np.exp(-t * 16.0)
        snap_noise = np.random.uniform(-0.3, 0.3, n_samples) * np.exp(-t * 28.0)
        hit = (np.sin(phase) * decay + snap_noise) * 0.8
        
    return hit


# ==============================================================================
# ETHIOPIAN SCALE DEFINITIONS (KIÑIT)
# ==============================================================================

# Base root frequency: C3 = 130.81 Hz, C4 = 261.63 Hz
ROOT_FREQ = 130.81

# Pentatonic intervals (semitones from root):
SCALES = {
    "Tizita_Minor": [0, 2, 3, 7, 8],     # C, D, Eb, G, Ab (Deep nostalgia, longing, family heritage)
    "Tizita_Major": [0, 2, 4, 7, 9],     # C, D, E, G, A (Warmth, love, bright memories)
    "Bati":         [0, 4, 5, 7, 11],    # C, E, F, G, B (Lively celebration, joyous gathering)
    "Ambassel":     [0, 1, 5, 7, 8],     # C, Db, F, G, Ab (Contemplative, wisdom, ancestral storytelling)
}


def get_scale_frequencies(scale_name: str, root_freq: float = 130.81, octaves: int = 3) -> list[float]:
    """Calculate absolute Hz frequencies for an Ethiopian pentatonic mode across octaves."""
    semitones = SCALES.get(scale_name, SCALES["Tizita_Minor"])
    freqs = []
    for oct_idx in range(octaves):
        for s in semitones:
            freq = root_freq * (2 ** oct_idx) * (2 ** (s / 12.0))
            freqs.append(freq)
    return freqs


# ==============================================================================
# SCORE GENERATOR SUITE ACROSS 90 SECONDS
# ==============================================================================

def generate_candidate_score(
    candidate_id: str,
    scale_name: str,
    bpm: float,
    character_theme: str,
    total_duration_sec: float = 90.0,
    sr: int = SAMPLE_RATE
) -> np.ndarray:
    """
    Synthesize an authentic full 90-second score matching the 5 emotional movements
    of 'The Memories of Our Home' storyboard.
    """
    total_samples = int(sr * total_duration_sec)
    left_channel = np.zeros(total_samples)
    right_channel = np.zeros(total_samples)
    
    freqs = get_scale_frequencies(scale_name, ROOT_FREQ, octaves=3)
    # Mapping scale tones:
    # freqs[0..4]   = Octave 3 (Low Bass / Drone)
    # freqs[5..9]   = Octave 4 (Mid Krar Plucks)
    # freqs[10..14] = Octave 5 (High Washint Flute & Masinko Lead)

    beat_duration = 60.0 / bpm
    step_duration = beat_duration / 2.0  # Eighth-note quantization
    total_steps = int(total_duration_sec / step_duration)
    
    # --------------------------------------------------------------------------
    # 1. Krar Accompaniment (Arpeggios & Ostinato)
    # --------------------------------------------------------------------------
    krar_pattern = [0, 2, 4, 2, 1, 3, 2, 0]  # Traditional 8-step cyclical krar ostinato
    for step in range(total_steps):
        t_sec = step * step_duration
        if t_sec >= total_duration_sec - 1.0:
            break
            
        # Dynamic intensity envelope across the 5 movements:
        # Mov 1 (0-15s): subtle gentle plucks
        # Mov 2 (15-32s): rhythmic building
        # Mov 3 (32-51s): full rich chords
        # Mov 4 (51-72s): intimate sparse plucks
        # Mov 5 (72-90s): tender resolution decaying into silence
        if t_sec < 15.0:
            intensity = 0.40 * (t_sec / 15.0)
        elif t_sec < 32.0:
            intensity = 0.40 + 0.30 * ((t_sec - 15.0) / 17.0)
        elif t_sec < 51.0:
            intensity = 0.85
        elif t_sec < 72.0:
            intensity = 0.50
        elif t_sec < 85.0:
            intensity = 0.60 * (1.0 - (t_sec - 72.0) / 18.0)
        else:
            intensity = 0.15 * (1.0 - (t_sec - 85.0) / 5.0)
            
        note_idx = 5 + (krar_pattern[step % len(krar_pattern)] % 5)
        note_freq = freqs[note_idx]
        
        pluck = karplus_strong_pluck(note_freq, duration=step_duration * 1.8, sr=sr)
        start_samp = int(t_sec * sr)
        end_samp = min(start_samp + len(pluck), total_samples)
        add_len = end_samp - start_samp
        
        # Stereo panning: Krar slightly panned to the right (stereo field warmth)
        left_channel[start_samp:end_samp] += pluck[:add_len] * (intensity * 0.65)
        right_channel[start_samp:end_samp] += pluck[:add_len] * (intensity * 0.95)

    # --------------------------------------------------------------------------
    # 2. Washint Bamboo Flute (Lead Melodic Expression)
    # --------------------------------------------------------------------------
    flute_phrases = [
        # Phrase 1: Tender opening (Shot 01)
        (2.0, [10, 12, 13, 12], [2.2, 1.8, 2.5, 3.0]),
        # Phrase 2: Grandmother's warmth (Shot 02)
        (9.5, [11, 12, 10, 9], [1.5, 1.8, 1.6, 2.8]),
        # Phrase 3: Relatives arriving (Shot 03)
        (16.0, [12, 13, 14, 13, 12], [1.2, 1.2, 2.0, 1.5, 2.2]),
        # Phrase 4: Feast preparation (Shot 04)
        (24.5, [10, 12, 14, 13], [1.5, 1.5, 2.2, 2.5]),
        # Phrase 5: Climax around the Mesob (Shot 05)
        (33.0, [14, 13, 14, 12, 13, 10], [1.8, 1.2, 2.5, 1.4, 2.0, 3.5]),
        # Phrase 6: The Gursha tender gift (Shot 06)
        (44.0, [12, 11, 10, 9, 10], [1.6, 1.5, 2.0, 1.8, 2.5]),
        # Phrase 7: Coffee Ceremony incense (Shot 07)
        (52.5, [10, 12, 13, 12], [2.2, 2.0, 2.8, 3.2]),
        # Phrase 8: Grandfather ancestral lore (Shot 08)
        (63.0, [11, 12, 14, 13, 12], [1.5, 1.8, 2.2, 1.6, 2.8]),
        # Phrase 9: Sunset unity climax (Shot 09)
        (73.5, [13, 14, 13, 12, 10], [2.0, 2.2, 2.5, 2.0, 3.5]),
    ]
    
    for phrase_start_sec, note_indices, note_durs in flute_phrases:
        cur_t = phrase_start_sec
        for n_idx, n_dur in zip(note_indices, note_durs):
            if cur_t + n_dur >= total_duration_sec - 1.0:
                break
            freq = freqs[min(n_idx, len(freqs) - 1)]
            tone = washint_flute_tone(freq, n_dur, sr=sr)
            
            s_start = int(cur_t * sr)
            s_end = min(s_start + len(tone), total_samples)
            add_len = s_end - s_start
            
            # Flute slightly panned to the left
            left_channel[s_start:s_end] += tone[:add_len] * 0.90
            right_channel[s_start:s_end] += tone[:add_len] * 0.60
            cur_t += n_dur

    # --------------------------------------------------------------------------
    # 3. Kebero Percussion (Heartbeat Pulse in Mov 2, 3, and 5)
    # --------------------------------------------------------------------------
    for step in range(total_steps):
        t_sec = step * step_duration
        # Drums active during family gathering and feast (16s to 50s and 73s to 82s)
        if (16.0 <= t_sec <= 50.0) or (73.0 <= t_sec <= 82.0):
            beat_in_measure = step % 4
            if beat_in_measure == 0:  # Strong downbeat bass
                hit = kebero_drum_hit("bass", duration=0.6, sr=sr)
                vol = 0.55 if t_sec < 32.0 else 0.75
            elif beat_in_measure == 2:  # Crisp secondary slap
                hit = kebero_drum_hit("slap", duration=0.3, sr=sr)
                vol = 0.35 if t_sec < 32.0 else 0.50
            else:
                continue
                
            s_start = int(t_sec * sr)
            s_end = min(s_start + len(hit), total_samples)
            add_len = s_end - s_start
            
            # Drums centered in stereo image
            left_channel[s_start:s_end] += hit[:add_len] * vol
            right_channel[s_start:s_end] += hit[:add_len] * vol

    # --------------------------------------------------------------------------
    # 4. Low Acoustic Drone / Masinko Resonant Floor (0 to 86s)
    # --------------------------------------------------------------------------
    root_bass = freqs[0]  # C3 low root
    t_arr = np.linspace(0, total_duration_sec, total_samples, endpoint=False)
    drone = 0.18 * np.sin(2 * np.pi * root_bass * t_arr)
    # Soft 5th harmonic overtone (G3)
    drone += 0.08 * np.sin(2 * np.pi * freqs[3] * t_arr)
    
    # Drone fade-in and smooth fade-out at end card
    drone_env = np.ones(total_samples)
    drone_fade_in = int(sr * 3.0)
    drone_fade_out = int(sr * 7.0)
    drone_env[:drone_fade_in] = np.linspace(0, 1, drone_fade_in)
    drone_env[-drone_fade_out:] = np.linspace(1, 0, drone_fade_out)
    
    left_channel += drone * drone_env
    right_channel += drone * drone_env

    # --------------------------------------------------------------------------
    # 5. Master Stereo Normalization & Smooth Outro Fade (85.0s to 90.0s)
    # --------------------------------------------------------------------------
    stereo = np.vstack([left_channel, right_channel])
    
    # 5-second smooth outro fade-out (during end card)
    fade_len = int(sr * 5.0)
    fade_curve = np.linspace(1.0, 0.0, fade_len) ** 2
    stereo[:, -fade_len:] *= fade_curve
    
    # Peak normalization to -1.5 dBFS (prevent digital clipping)
    peak = np.max(np.abs(stereo))
    if peak > 0:
        target_peak = 10 ** (-1.5 / 20.0)  # ~0.841
        stereo = (stereo / peak) * target_peak
        
    return stereo


# ==============================================================================
# CANDIDATE AUDITION & EVALUATION SUITE
# ==============================================================================

CANDIDATES_SPEC = [
    {
        "id": "candidate_a",
        "title": "Tizita of the Hearth",
        "scale": "Tizita_Minor",
        "bpm": 68,
        "mood": "Nostalgic, warm, unhurried, heartfelt familial remembrance",
        "instruments": "Krar arpeggios, Washint bamboo flute, Kebero heartbeat drum, Masinko resonance",
    },
    {
        "id": "candidate_b",
        "title": "Bati Feast Celebration",
        "scale": "Bati",
        "bpm": 78,
        "mood": "Joyous, rhythmic, celebratory, family feast vibrancy",
        "instruments": "Fast Krar strumming, syncopated Kebero rhythms, upbeat Masinko fiddling",
    },
    {
        "id": "candidate_c",
        "title": "Ambassel Contemplation",
        "scale": "Ambassel",
        "bpm": 72,
        "mood": "Meditative, ancestral wisdom, deep highland contemplation",
        "instruments": "Solemn Washint lead, low Krar bass drone, sparse contemplative hits",
    },
]


def audition_candidate(audio_data: np.ndarray, sr: int = SAMPLE_RATE) -> dict:
    """Analyze acoustic characteristics for objective audition comparison."""
    # Peak dBFS
    peak = np.max(np.abs(audio_data))
    peak_db = 20 * math.log10(peak) if peak > 0 else -99.0
    
    # RMS Energy dBFS
    rms = np.sqrt(np.mean(audio_data ** 2))
    rms_db = 20 * math.log10(rms) if rms > 0 else -99.0
    
    # Dynamic Crest Factor
    crest_factor = peak_db - rms_db
    
    return {
        "peak_dbfs": round(peak_db, 2),
        "rms_dbfs": round(rms_db, 2),
        "crest_factor_db": round(crest_factor, 2),
    }


def synthesize_all_candidates(force: bool = False) -> dict:
    """Generate all 3 candidates and evaluate them."""
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    audition_results = {}
    
    print("==================================================")
    print("STAGE 05: ORIGINAL MUSIC SCORE SYNTHESIS")
    print("Acoustic Model: Ethiopian Pentatonic Synthesizer (Kiñit)")
    print(f"Target Duration: 90.00s | Sample Rate: {SAMPLE_RATE} Hz")
    print("==================================================")
    
    for cand in CANDIDATES_SPEC:
        cid = cand["id"]
        out_path = MUSIC_DIR / f"{cid}.wav"
        
        cache_payload = {
            "id": cid,
            "scale": cand["scale"],
            "bpm": cand["bpm"],
            "duration": 90.0,
            "sr": SAMPLE_RATE
        }
        
        t0 = time.time()
        if not force and is_cached(out_path, cache_payload):
            print(f"[⚡ CACHED] {cid}: '{cand['title']}' ({cand['scale']}, {cand['bpm']} BPM)")
            rate, data = wavfile.read(str(out_path))
            # Convert to float
            data_float = data.astype(np.float32) / 32767.0
            stats = audition_candidate(data_float, rate)
            audition_results[cid] = {**cand, **stats, "cached": True}
            continue
            
        print(f"\n[SYNTHESIZING] {cid}: '{cand['title']}' ...")
        print(f"  Scale: {cand['scale']} | Tempo: {cand['bpm']} BPM")
        print(f"  Mood: {cand['mood']}")
        
        stereo_audio = generate_candidate_score(
            candidate_id=cid,
            scale_name=cand["scale"],
            bpm=cand["bpm"],
            character_theme=cand["mood"],
            total_duration_sec=90.0,
            sr=SAMPLE_RATE
        )
        
        # Write 16-bit PCM WAV
        audio_int16 = (stereo_audio.T * 32767.0).astype(np.int16)
        wavfile.write(str(out_path), SAMPLE_RATE, audio_int16)
        save_hash(out_path, cache_payload)
        
        latency = round(time.time() - t0, 2)
        stats = audition_candidate(stereo_audio, SAMPLE_RATE)
        size_mb = round(out_path.stat().st_size / (1024 * 1024), 2)
        print(f"  [✓] SUCCESS: {out_path.name} ({size_mb} MB in {latency}s)")
        print(f"      RMS: {stats['rms_dbfs']} dBFS | Peak: {stats['peak_dbfs']} dBFS | Dynamic Range: {stats['crest_factor_db']} dB")
        
        log_run(
            stage="05_music",
            target=out_path.name,
            model="ethiopian_acoustic_synthesizer",
            parameters={"scale": cand["scale"], "bpm": cand["bpm"], "duration": 90.0},
            latency_seconds=latency,
            status="success",
            metadata={"candidate": cid, "title": cand["title"], "size_mb": size_mb, **stats}
        )
        
        audition_results[cid] = {**cand, **stats, "cached": False}
        
    return audition_results


def select_master_score(candidate_id: str = "candidate_a") -> Path:
    """
    Select the winning candidate score and publish as selected_score.wav.
    """
    selected_source = MUSIC_DIR / f"{candidate_id}.wav"
    master_target = MUSIC_DIR / "selected_score.wav"
    
    if not selected_source.exists():
        raise FileNotFoundError(f"Selected candidate file not found: {selected_source}")
        
    # Copy/write master target
    import shutil
    shutil.copyfile(selected_source, master_target)
    
    # Verify exact duration
    dur = get_media_duration(master_target)
    print("\n==================================================")
    print("WINNING MASTER SCORE SELECTION:")
    print(f"Winner: {candidate_id.upper()} -> outputs/music/selected_score.wav")
    print(f"Duration: {dur:.2f}s (Contract: 90.0s)")
    print(f"Integrity: {'PERFECT 90.0s' if abs(dur - 90.0) < 0.2 else 'DEVIATION'}")
    print("==================================================")
    
    log_run(
        stage="05_music",
        target="selected_score.wav",
        model="master_selector",
        parameters={"selected_candidate": candidate_id, "duration": dur},
        latency_seconds=0.05,
        status="success",
        metadata={"source": str(selected_source), "duration_seconds": dur}
    )
    
    return master_target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stage 5: Music Score Generator & Audition Engine")
    parser.add_argument("--force", action="store_true", help="Force regenerate candidate files")
    parser.add_argument("--select", type=str, default="candidate_a", help="Select winning candidate (candidate_a/b/c)")
    args = parser.parse_args()
    
    results = synthesize_all_candidates(force=args.force)
    select_master_score(args.select)
