"""
Helper for discovering and invoking FFmpeg across system and virtual environments.
Supports native system ffmpeg or imageio_ffmpeg binary.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def get_ffmpeg_path() -> str:
    """
    Locate the best available FFmpeg executable.
    Checks:
    1. System PATH
    2. imageio-ffmpeg bundled binary
    """
    # 1. System PATH check
    system_path = shutil.which("ffmpeg")
    if system_path:
        return system_path

    # 2. imageio_ffmpeg check
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except ImportError:
        pass

    raise RuntimeError(
        "FFmpeg binary not found. Please install ffmpeg or run 'pip install imageio-ffmpeg'."
    )


def run_ffmpeg(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """
    Execute FFmpeg with the discovered executable.
    """
    ffmpeg_exe = get_ffmpeg_path()
    cmd = [ffmpeg_exe] + args
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def get_media_duration(file_path: Path) -> float:
    """
    Extract accurate duration in seconds from any audio/video file using FFmpeg.
    """
    import re
    res = run_ffmpeg(["-i", str(file_path)], check=False)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0



if __name__ == "__main__":
    path = get_ffmpeg_path()
    print(f"FFmpeg binary discovered at: {path}")
    result = run_ffmpeg(["-version"])
    first_line = result.stdout.splitlines()[0] if result.stdout else "unknown"
    print(f"FFmpeg version: {first_line}")
