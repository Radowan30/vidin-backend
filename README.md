# VidIn - LinkedIn Post to Video Generator

Transform your LinkedIn posts into engaging animated videos with voiceover and synchronized subtitles.

## Features

- **AI-Powered Script Generation**: Uses Groq's LLM to analyze your LinkedIn post and create a scene-by-scene video script
- **Dynamic Animations**: Generates HTML/CSS/JavaScript animations using GSAP (GreenSock Animation Platform)
- **Professional Voiceover**: ElevenLabs text-to-speech with word-level timestamps
- **Synchronized Subtitles**: Each word highlights in yellow as it's spoken
- **Multiple Aspect Ratios**: Support for 16:9 (YouTube), 9:16 (TikTok/Reels), and 1:1 (Instagram)
- **High-Quality Output**: 30fps MP4 video with AAC audio

## Prerequisites

Before running VidIn, ensure you have the following installed:

### 1. Python 3.9+
Download from [python.org](https://www.python.org/downloads/)

### 2. FFmpeg
FFmpeg is required for audio processing and video compilation.

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or using Scoop
scoop install ffmpeg

# Or download manually from https://ffmpeg.org/download.html
# Add the bin folder to your PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

### 3. API Keys

You'll need API keys from:

- **Groq**: Get your API key at [console.groq.com](https://console.groq.com)
- **ElevenLabs**: Get your API key at [elevenlabs.io](https://elevenlabs.io)

## Installation

1. **Clone or navigate to the project directory:**
```bash
cd "Cursor Hackathon - VidIn"
```

2. **Create a virtual environment (recommended):**
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\Activate.ps1
# Or for Command Prompt
.\venv\Scripts\activate.bat

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**
```bash
playwright install chromium
```

5. **Configure environment variables:**

Edit the `.env` file and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
GROQ_MODEL=llama-3.3-70b-versatile
```

**Voice ID Options:**
- `21m00Tcm4TlvDq8ikWAM` - Rachel (default, female)
- `AZnzlk1XvdvUeBnXmlld` - Domi (female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (female)
- `ErXwobaYiN019PkySvjV` - Antoni (male)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (female)
- `TxGEqnHWrfWFTfGW9XjX` - Josh (male)
- `VR6AewLTigWG4xSOukaG` - Arnold (male)
- `pNInz6obpgDQGcFmaJgB` - Adam (male)

Find more voices at [ElevenLabs Voice Library](https://elevenlabs.io/voice-library)

## Usage

### Command Line Interface

**Using text directly:**
```bash
python main.py -t "🚀 Just shipped a feature that reduced API response time by 73%! Here's what we did..." -r 16:9
```

**Using a text file:**
```bash
python main.py -f my_post.txt -r 9:16
```

**Interactive mode:**
```bash
python main.py --interactive
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-t, --text` | LinkedIn post text | - |
| `-f, --file` | Path to file containing post | - |
| `-r, --ratio` | Aspect ratio (1:1, 9:16, 16:9) | 16:9 |
| `--fps` | Frames per second | 30 |
| `--id` | Custom video ID | Auto-generated |
| `-i, --interactive` | Interactive mode | - |

### Python API

```python
from main import VidIn
import asyncio

# Create VidIn instance
vidin = VidIn()

# Your LinkedIn post
post = """
🚀 Just shipped a feature that reduced our API response time by 73%!

Here's what we did:
1. Implemented Redis caching for frequent queries
2. Optimized database indexes
3. Added connection pooling
4. Compressed API responses

The result? Our users are happier, our servers are cooler, and our costs dropped by 40%.

Sometimes the biggest wins come from the smallest optimizations. 💡

#Engineering #Performance #Optimization
"""

# Generate video
output_path = asyncio.run(vidin.generate_video(
    linkedin_post=post,
    aspect_ratio="16:9",  # or "9:16" or "1:1"
    fps=30
))

print(f"Video saved to: {output_path}")
```

## Output

Generated videos are saved in the `videos/` directory with unique IDs:
```
videos/vidin_abc12345_20240115_143022.mp4
```

## Project Structure

```
Cursor Hackathon - VidIn/
├── main.py                 # Main orchestration script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (API keys)
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── script_generator.py # Groq API for script generation
│   ├── code_generator.py   # Groq API for animation code
│   ├── audio_generator.py  # ElevenLabs API for voiceover
│   └── video_generator.py  # Playwright + FFmpeg for rendering
├── temp/                   # Temporary files (auto-cleaned)
├── templates/              # HTML templates
└── videos/                 # Generated videos output
```

## How It Works

1. **Script Generation**: Your LinkedIn post is sent to Groq's LLM, which analyzes the content and generates a detailed scene-by-scene script with:
   - Visual descriptions for each scene
   - Animation specifications (types, directions, colors)
   - Voiceover text for each scene

2. **Code Generation**: The script is processed by another Groq API call that generates HTML/CSS/JavaScript code using GSAP for smooth animations.

3. **Audio Generation**: ElevenLabs converts the voiceover text to speech with word-level timestamps for subtitle synchronization.

4. **Video Rendering**: Playwright loads the HTML, captures frames synchronized with the audio, and FFmpeg compiles everything into the final video.

## Troubleshooting

### "FFmpeg not found"
Make sure FFmpeg is installed and in your system PATH. Run `ffmpeg -version` to verify.

### "Playwright browsers not installed"
Run `playwright install chromium` to install the required browser.

### "API key error"
Verify your API keys in the `.env` file. Make sure there are no extra spaces or quotes.

### "Video generation is slow"
Video rendering captures frames at the specified FPS. For faster preview, try:
```bash
python main.py -t "Your post" --fps 15
```

### "ElevenLabs rate limit"
Free tier has limited characters/month. Consider upgrading or shortening your posts.

## Tips for Best Results

1. **Keep posts concise**: 100-300 words work best
2. **Use clear structure**: Numbered lists and bullet points translate well to scenes
3. **Include emotional hooks**: Emojis and impactful statements make better visuals
4. **Test with shorter posts first**: Helps you iterate on style preferences

## License

MIT License - feel free to use and modify for your projects.

## Credits

Built with:
- [Groq](https://groq.com) - Ultra-fast LLM inference
- [ElevenLabs](https://elevenlabs.io) - AI voice generation
- [GSAP](https://greensock.com/gsap/) - Professional-grade animations
- [Playwright](https://playwright.dev) - Browser automation
- [FFmpeg](https://ffmpeg.org) - Video/audio processing

