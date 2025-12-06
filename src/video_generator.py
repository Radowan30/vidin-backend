"""
Video Generator Module
Renders HTML animations to video using Playwright and FFmpeg
"""

import os
import json
import subprocess
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page


@dataclass
class VideoConfig:
    """Configuration for video generation"""
    width: int
    height: int
    fps: int = 30
    quality: int = 23  # CRF value for FFmpeg (lower = better quality)
    output_format: str = "mp4"


class VideoGenerator:
    """Generates video from HTML animations using Playwright and FFmpeg"""
    
    def __init__(self, temp_dir: str = "temp", output_dir: str = "videos"):
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def _get_dimensions(self, aspect_ratio: str) -> tuple:
        """Returns width, height for the aspect ratio"""
        dimensions = {
            "1:1": (1080, 1080),
            "9:16": (1080, 1920),
            "16:9": (1920, 1080)
        }
        return dimensions.get(aspect_ratio, (1920, 1080))
    
    async def _init_browser(self, width: int, height: int):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1
        )
    
    async def _close_browser(self):
        """Close Playwright browser and cleanup resources"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
        except Exception:
            pass
        
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception:
            pass
        
        try:
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception:
            pass
    
    async def render_video(
        self,
        html_path: str,
        audio_path: str,
        scene_durations: List[float],
        subtitle_data: List[Dict[str, Any]],
        aspect_ratio: str = "16:9",
        fps: int = 30,
        video_id: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> str:
        """
        Render HTML animation to video with audio
        
        Args:
            html_path: Path to the HTML file
            audio_path: Path to the merged audio file
            scene_durations: Duration of each scene in seconds
            subtitle_data: Word timing data for subtitles
            aspect_ratio: Video aspect ratio
            fps: Frames per second
            video_id: Optional unique ID for the video
            progress_callback: Optional callback(progress_percent, message) for progress updates
        
        Returns:
            Path to the generated video file
        """
        width, height = self._get_dimensions(aspect_ratio)
        config = VideoConfig(width=width, height=height, fps=fps)
        
        # Generate unique video ID if not provided
        if not video_id:
            video_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate total duration
        total_duration = sum(scene_durations)
        total_frames = int(total_duration * fps)
        
        print(f"Rendering video: {total_duration:.2f}s, {total_frames} frames")
        
        # Initialize browser
        await self._init_browser(width, height)
        
        try:
            # Set up console message listener to catch JavaScript errors
            console_errors = []
            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
            self.page.on("console", handle_console)
            
            # Load HTML file
            html_file_url = f"file:///{Path(html_path).resolve().as_posix()}"
            await self.page.goto(html_file_url)
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(1.5)  # Extra wait for fonts, GSAP library, and resources
            
            # Check for JavaScript errors
            if console_errors:
                print(f"  ⚠ JavaScript console errors detected: {console_errors[:3]}")
            
            # Wait for videoController to be defined (retry up to 10 times)
            for attempt in range(10):
                is_ready = await self.page.evaluate("typeof window.videoController !== 'undefined'")
                if is_ready:
                    print(f"  ✓ Video controller initialized")
                    break
                print(f"  Waiting for video controller to initialize (attempt {attempt + 1}/10)...")
                await asyncio.sleep(0.5)
            else:
                # Try to get more info about what went wrong
                page_errors = await self.page.evaluate("window._pageErrors || []")
                raise Exception(f"Video controller failed to initialize. Console errors: {console_errors}. Page errors: {page_errors}")
            
            # Inject scene durations and subtitle data with error handling
            try:
                await asyncio.wait_for(
                    self.page.evaluate(f"""
                        window.videoController.setSceneDurations({json.dumps(scene_durations, ensure_ascii=True)});
                        window.videoController.setSubtitleData({json.dumps(subtitle_data, ensure_ascii=True)});
                    """),
                    timeout=10.0
                )
                print(f"  ✓ Timing data injected")
            except asyncio.TimeoutError:
                raise Exception("Timeout injecting timing data - JavaScript may be hanging")
            except Exception as e:
                raise Exception(f"Failed to inject timing data: {e}")
            
            # Rebuild the master timeline with new durations (with timeout)
            try:
                await asyncio.wait_for(
                    self.page.evaluate("window.videoController.rebuild();"),
                    timeout=10.0
                )
                print(f"  ✓ Timeline rebuilt")
            except asyncio.TimeoutError:
                raise Exception("Timeout rebuilding timeline - JavaScript may have infinite loop")
            except Exception as e:
                raise Exception(f"Failed to rebuild timeline: {e}")
            
            # Give time for timeline to rebuild
            await asyncio.sleep(0.3)
            
            # Start the video playback (with timeout)
            try:
                await asyncio.wait_for(
                    self.page.evaluate("window.videoController.start();"),
                    timeout=10.0
                )
                print(f"  ✓ Playback started")
            except asyncio.TimeoutError:
                raise Exception("Timeout starting playback - JavaScript may be hanging")
            except Exception as e:
                raise Exception(f"Failed to start playback: {e}")
            
            # Capture frames
            frames_dir = self.temp_dir / f"frames_{video_id}"
            frames_dir.mkdir(exist_ok=True)
            
            print(f"  Capturing {total_frames} frames...")
            
            # Calculate frame times
            frame_time = 1.0 / fps
            
            # Capture first frame and verify it looks reasonable
            first_frame_path = frames_dir / "frame_000000.png"
            await self.page.evaluate("window.videoController.seek(0);")
            await self._update_subtitle_highlighting(0, subtitle_data)
            await asyncio.sleep(0.05)
            await self.page.screenshot(
                path=str(first_frame_path),
                type="png",
                clip={"x": 0, "y": 0, "width": width, "height": height}
            )
            
            # Check first frame size (should be > 10KB for a non-blank frame)
            first_frame_size = first_frame_path.stat().st_size
            if first_frame_size < 10000:  # Less than 10KB suggests blank/error page
                print(f"  ⚠ Warning: First frame is very small ({first_frame_size} bytes) - page may not be rendering correctly")
            else:
                print(f"  ✓ First frame captured ({first_frame_size / 1024:.1f} KB)")
            
            # Continue with remaining frames (start from 1 since we did 0)
            for frame_num in range(1, total_frames):
                try:
                    current_time = frame_num * frame_time
                    
                    # Seek to the current time
                    await self.page.evaluate(f"window.videoController.seek({current_time});")
                    
                    # Update subtitle highlighting based on current time
                    await self._update_subtitle_highlighting(current_time, subtitle_data)
                    
                    # Small delay to let animations render
                    await asyncio.sleep(0.016)  # ~60fps rendering time
                    
                    # Capture frame
                    frame_path = frames_dir / f"frame_{frame_num:06d}.png"
                    await self.page.screenshot(
                        path=str(frame_path),
                        type="png",
                        clip={"x": 0, "y": 0, "width": width, "height": height}
                    )
                    
                    # Progress indicator (every 5 seconds of video = every fps*5 frames)
                    if frame_num % (fps * 5) == 0:
                        render_progress = (frame_num / total_frames) * 100
                        elapsed_video_time = frame_num / fps
                        print(f"  Progress: {render_progress:.1f}% ({elapsed_video_time:.1f}s / {total_duration:.1f}s)")
                        
                        # Call progress callback if provided
                        # Map rendering progress (0-100%) to 60-95% of overall progress
                        if progress_callback:
                            overall_progress = 60 + int(render_progress * 0.35)  # 60% + up to 35% = 95%
                            progress_callback(overall_progress, f"Rendering frames... {render_progress:.0f}%")
                except Exception as e:
                    print(f"  ⚠ Error capturing frame {frame_num}: {e}")
                    # Continue with next frame instead of failing completely
                    continue
            
            # Verify frames were captured
            captured_frames = list(frames_dir.glob("frame_*.png"))
            print(f"  Frame capture complete. Captured {len(captured_frames)} frames.")
            
            if len(captured_frames) == 0:
                raise Exception("No frames were captured! The HTML page may have rendering issues.")
            
            if len(captured_frames) < total_frames * 0.9:  # Less than 90% captured
                print(f"  ⚠ Warning: Only {len(captured_frames)}/{total_frames} frames captured")
            
            print("  Compiling video with FFmpeg...")
            
            # Compile frames to video with audio
            output_path = self.output_dir / f"{video_id}.mp4"
            await self._compile_video(
                frames_dir=str(frames_dir),
                audio_path=audio_path,
                output_path=str(output_path),
                config=config
            )
            
            # Verify output video was created
            if not output_path.exists():
                raise Exception(f"Video compilation failed - output file not created: {output_path}")
            
            output_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Video compiled: {output_path} ({output_size_mb:.1f} MB)")
            
            # Clean up frames
            self._cleanup_frames(str(frames_dir))
            
            return str(output_path)
            
        finally:
            await self._close_browser()
    
    async def _update_subtitle_highlighting(
        self,
        current_time: float,
        subtitle_data: List[Dict[str, Any]]
    ):
        """Update subtitle highlighting based on current time"""
        # Find the current scene's subtitle data
        current_subtitle = None
        for subtitle in subtitle_data:
            if subtitle["start_time"] <= current_time <= subtitle["end_time"]:
                current_subtitle = subtitle
                break
        
        if not current_subtitle:
            # Clear subtitles if we're between scenes
            await self.page.evaluate("window.videoController.clearSubtitle();")
            return
        
        # Find which word should be highlighted
        text = current_subtitle["text"]
        words = current_subtitle.get("words", [])
        
        highlight_index = -1
        for i, word_data in enumerate(words):
            word_start = word_data["start"]
            word_end = word_data["end"]
            if word_start <= current_time <= word_end + 0.1:  # Small buffer
                highlight_index = i
                break
            elif current_time > word_end:
                highlight_index = i  # Keep last word highlighted until next
        
        # Update subtitle with highlighting
        await self.page.evaluate(
            f"window.videoController.updateSubtitle({json.dumps(text)}, {highlight_index});"
        )
    
    async def _compile_video(
        self,
        frames_dir: str,
        audio_path: str,
        output_path: str,
        config: VideoConfig
    ):
        """Compile frames and audio into final video using FFmpeg"""
        
        # FFmpeg command to create video from frames and add audio
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(config.fps),
            "-i", f"{frames_dir}/frame_%06d.png",
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", str(config.quality),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
    
    def _cleanup_frames(self, frames_dir: str):
        """Clean up frame images"""
        frames_path = Path(frames_dir)
        if frames_path.exists():
            for frame_file in frames_path.glob("*.png"):
                frame_file.unlink()
            frames_path.rmdir()
    
    def cleanup_temp_files(self, video_id: str):
        """Clean up all temporary files for a video"""
        # Clean up frames directory
        frames_dir = self.temp_dir / f"frames_{video_id}"
        self._cleanup_frames(str(frames_dir))
        
        # Clean up HTML file
        html_path = self.temp_dir / f"{video_id}.html"
        if html_path.exists():
            html_path.unlink()
        
        # Clean up audio files
        for audio_file in self.temp_dir.glob(f"scene_*_audio.mp3"):
            audio_file.unlink()
        
        merged_audio = self.temp_dir / f"{video_id}_merged.mp3"
        if merged_audio.exists():
            merged_audio.unlink()


def generate_video_sync(
    html_path: str,
    audio_path: str,
    scene_durations: List[float],
    subtitle_data: List[Dict[str, Any]],
    aspect_ratio: str = "16:9",
    fps: int = 30,
    video_id: Optional[str] = None,
    temp_dir: str = "temp",
    output_dir: str = "videos"
) -> str:
    """
    Synchronous wrapper for video generation
    
    This function can be called from synchronous code.
    """
    generator = VideoGenerator(temp_dir=temp_dir, output_dir=output_dir)
    
    return asyncio.run(generator.render_video(
        html_path=html_path,
        audio_path=audio_path,
        scene_durations=scene_durations,
        subtitle_data=subtitle_data,
        aspect_ratio=aspect_ratio,
        fps=fps,
        video_id=video_id
    ))


if __name__ == "__main__":
    # Test the video generator with a simple HTML file
    import asyncio
    
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
        <style>
            body {
                width: 1920px;
                height: 1080px;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: sans-serif;
            }
            .text {
                color: white;
                font-size: 72px;
                opacity: 0;
            }
        </style>
    </head>
    <body>
        <div class="text">Test Video</div>
        <script>
            let masterTimeline = gsap.timeline({ paused: true });
            masterTimeline.to('.text', { opacity: 1, duration: 1 });
            masterTimeline.to('.text', { scale: 1.2, duration: 1 });
            masterTimeline.to('.text', { rotation: 360, duration: 1 });
            
            window.videoController = {
                seek: (time) => masterTimeline.seek(time),
                start: () => masterTimeline.play(),
                setSceneDurations: () => {},
                setSubtitleData: () => {},
                rebuild: () => {},
                updateSubtitle: () => {},
                clearSubtitle: () => {}
            };
        </script>
    </body>
    </html>
    """
    
    # Save test HTML
    test_html_path = Path("temp/test.html")
    test_html_path.parent.mkdir(exist_ok=True)
    test_html_path.write_text(test_html)
    
    print("Test HTML saved. Run with actual audio to test video generation.")

