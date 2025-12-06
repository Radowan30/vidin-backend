"""
Utility functions for VidIn
"""

import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_video_id(prefix: str = "vidin") -> str:
    """Generate a unique video ID"""
    unique_part = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{unique_part}_{timestamp}"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    return sanitized[:200]


def ensure_directory(path: str) -> Path:
    """Ensure a directory exists"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to MM:SS format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def get_dimensions(aspect_ratio: str) -> tuple:
    """Get width and height for an aspect ratio"""
    dimensions = {
        "1:1": (1080, 1080),
        "9:16": (1080, 1920),
        "16:9": (1920, 1080)
    }
    return dimensions.get(aspect_ratio, (1920, 1080))


def validate_env_vars() -> dict:
    """Validate required environment variables"""
    required_vars = {
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
    }
    
    optional_vars = {
        "ELEVENLABS_VOICE_ID": os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        "GROQ_MODEL": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please check your .env file."
        )
    
    return {**required_vars, **optional_vars}


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and accessible"""
    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_ffprobe_installed() -> bool:
    """Check if FFprobe is installed and accessible"""
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def print_system_check():
    """Print system check results"""
    print("\n🔍 System Check")
    print("=" * 40)
    
    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python: {python_version} {'✓' if sys.version_info >= (3, 9) else '⚠ (3.9+ recommended)'}")
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg_installed()
    print(f"FFmpeg: {'✓ Installed' if ffmpeg_ok else '✗ Not found'}")
    
    # Check FFprobe
    ffprobe_ok = check_ffprobe_installed()
    print(f"FFprobe: {'✓ Installed' if ffprobe_ok else '✗ Not found'}")
    
    # Check environment variables
    try:
        env_vars = validate_env_vars()
        print(f"Groq API Key: {'✓ Set' if env_vars['GROQ_API_KEY'] else '✗ Missing'}")
        print(f"ElevenLabs API Key: {'✓ Set' if env_vars['ELEVENLABS_API_KEY'] else '✗ Missing'}")
        print(f"Voice ID: {env_vars['ELEVENLABS_VOICE_ID']}")
        print(f"Groq Model: {env_vars['GROQ_MODEL']}")
    except ValueError as e:
        print(f"Environment: ✗ {e}")
    
    print("=" * 40)
    
    if not ffmpeg_ok or not ffprobe_ok:
        print("\n⚠ Please install FFmpeg to continue.")
        print("  Windows: choco install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
    
    return ffmpeg_ok and ffprobe_ok


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print_system_check()

