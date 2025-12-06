"""
VidIn - LinkedIn Post to Video Generator

Main orchestration script that coordinates all modules to generate
engaging animated videos from LinkedIn posts.
"""

import os
import sys
import json
import uuid
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.script_generator import ScriptGenerator, VideoScript
from src.code_generator import CodeGenerator
from src.audio_generator import AudioGenerator, SceneAudio
from src.video_generator import VideoGenerator


class VidIn:
    """Main application class for LinkedIn post to video generation"""
    
    VALID_ASPECT_RATIOS = ["1:1", "9:16", "16:9"]
    
    def __init__(self, temp_dir: str = "temp", output_dir: str = "videos"):
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize generators
        self.script_generator = ScriptGenerator()
        self.code_generator = CodeGenerator()
        self.audio_generator = AudioGenerator(temp_dir=temp_dir)
        self.video_generator = VideoGenerator(temp_dir=temp_dir, output_dir=output_dir)
        
        print("✓ VidIn initialized successfully")
    
    def validate_aspect_ratio(self, aspect_ratio: str) -> str:
        """Validate and normalize aspect ratio"""
        if aspect_ratio not in self.VALID_ASPECT_RATIOS:
            raise ValueError(
                f"Invalid aspect ratio: {aspect_ratio}. "
                f"Must be one of: {', '.join(self.VALID_ASPECT_RATIOS)}"
            )
        return aspect_ratio
    
    async def generate_video(
        self,
        linkedin_post: str,
        aspect_ratio: str = "16:9",
        fps: int = 30,
        video_id: Optional[str] = None
    ) -> str:
        """
        Generate a video from a LinkedIn post
        
        Args:
            linkedin_post: The text content of the LinkedIn post
            aspect_ratio: Video aspect ratio ("1:1", "9:16", "16:9")
            fps: Frames per second (default: 30)
            video_id: Optional custom video ID
        
        Returns:
            Path to the generated video file
        """
        # Validate inputs
        aspect_ratio = self.validate_aspect_ratio(aspect_ratio)
        
        # Generate unique ID
        if not video_id:
            video_id = f"vidin_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n{'='*60}")
        print(f"VidIn Video Generation")
        print(f"{'='*60}")
        print(f"Video ID: {video_id}")
        print(f"Aspect Ratio: {aspect_ratio}")
        print(f"FPS: {fps}")
        print(f"{'='*60}\n")
        
        try:
            # Step 1: Generate script
            print("📝 Step 1/5: Generating video script...")
            script = self.script_generator.generate_script(linkedin_post, aspect_ratio)
            print(f"   ✓ Generated script with {script.total_scenes} scenes")
            print(f"   Theme: {script.theme}, Font: {script.font_style}")
            for scene in script.scenes:
                print(f"   Scene {scene.scene_number}: {scene.scene_title}")
            
            # Step 2: Generate animation code
            print("\n🎨 Step 2/5: Generating animation code...")
            html_code = self.code_generator.generate_code(script, aspect_ratio)
            print(f"   ✓ Generated HTML/CSS/JS animation code")
            
            # Step 3: Generate audio for each scene
            print("\n🎵 Step 3/5: Generating voiceover audio...")
            scenes_data = [
                {"scene_number": s.scene_number, "voiceover_text": s.voiceover_text}
                for s in script.scenes
            ]
            scene_audios = self.audio_generator.generate_all_scene_audio(
                scenes=scenes_data,
                padding_seconds=1.0  # 1 second pause between scenes
            )
            print(f"   ✓ Generated audio for {len(scene_audios)} scenes")
            
            # Calculate scene durations and subtitle data
            scene_durations = [sa.duration for sa in scene_audios]
            total_duration = sum(scene_durations)
            print(f"   Total audio duration: {total_duration:.2f}s")
            
            # Build subtitle data with proper time offsets
            subtitle_data = []
            time_offset = 0.0
            for sa in scene_audios:
                subtitle_info = self.audio_generator.get_subtitle_data_for_scene(sa, time_offset)
                subtitle_data.append(subtitle_info)
                time_offset += sa.duration
            
            # Step 4: Update HTML with timing data
            print("\n⏱️  Step 4/5: Synchronizing timing data...")
            html_code = self.code_generator.update_html_with_timing(
                html_code, scene_durations, subtitle_data
            )
            
            # Validate HTML has content
            if "__PLACEHOLDER__" in html_code or len(html_code) < 5000:
                print(f"   ⚠ Warning: HTML may have issues (size: {len(html_code)} bytes)")
            
            # Check that scenes were injected
            scene_count = html_code.count('class="scene"')
            if scene_count == 0:
                raise Exception("HTML generation failed - no scenes found in output")
            print(f"   ✓ HTML contains {scene_count} scenes")
            
            # Save HTML file
            html_path = self.temp_dir / f"{video_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_code)
            print(f"   ✓ Saved HTML to {html_path} ({len(html_code) / 1024:.1f} KB)")
            
            # Merge all audio files
            merged_audio_path = self.temp_dir / f"{video_id}_merged.mp3"
            self.audio_generator.merge_all_audio(scene_audios, str(merged_audio_path))
            print(f"   ✓ Merged audio to {merged_audio_path}")
            
            # Step 5: Render video
            print("\n🎬 Step 5/5: Rendering video...")
            print(f"   This may take a few minutes for {int(total_duration * fps)} frames...")
            
            output_path = await self.video_generator.render_video(
                html_path=str(html_path),
                audio_path=str(merged_audio_path),
                scene_durations=scene_durations,
                subtitle_data=subtitle_data,
                aspect_ratio=aspect_ratio,
                fps=fps,
                video_id=video_id
            )
            
            print(f"\n{'='*60}")
            print(f"✅ Video generated successfully!")
            print(f"📁 Output: {output_path}")
            print(f"{'='*60}\n")
            
            # Cleanup temporary files
            print("🧹 Cleaning up temporary files...")
            self._cleanup(video_id, scene_audios, html_path, merged_audio_path)
            print("   ✓ Cleanup complete")
            
            return output_path
            
        except Exception as e:
            print(f"\n❌ Error during video generation: {e}")
            raise
    
    def _cleanup(
        self,
        video_id: str,
        scene_audios: list,
        html_path: Path,
        merged_audio_path: Path
    ):
        """Clean up all temporary files"""
        # Clean up scene audio files
        self.audio_generator.cleanup(scene_audios)
        
        # Clean up HTML file
        if html_path.exists():
            html_path.unlink()
        
        # Clean up merged audio
        if merged_audio_path.exists():
            merged_audio_path.unlink()
        
        # Clean up any remaining files in temp
        for f in self.temp_dir.glob(f"*{video_id}*"):
            try:
                if f.is_file():
                    f.unlink()
                elif f.is_dir():
                    import shutil
                    shutil.rmtree(f)
            except:
                pass


def generate_video_sync(
    linkedin_post: str,
    aspect_ratio: str = "16:9",
    fps: int = 30,
    video_id: Optional[str] = None
) -> str:
    """
    Synchronous wrapper for video generation
    
    This function can be called from synchronous code.
    """
    vidin = VidIn()
    return asyncio.run(vidin.generate_video(
        linkedin_post=linkedin_post,
        aspect_ratio=aspect_ratio,
        fps=fps,
        video_id=video_id
    ))


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="VidIn - Generate engaging videos from LinkedIn posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -t "Your LinkedIn post text here" -r 16:9
  python main.py -f post.txt -r 9:16 --fps 60
  python main.py --interactive
        """
    )
    
    parser.add_argument(
        "-t", "--text",
        type=str,
        help="LinkedIn post text (enclose in quotes)"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to file containing LinkedIn post text"
    )
    
    parser.add_argument(
        "-r", "--ratio",
        type=str,
        default="16:9",
        choices=["1:1", "9:16", "16:9"],
        help="Video aspect ratio (default: 16:9)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)"
    )
    
    parser.add_argument(
        "--id",
        type=str,
        help="Custom video ID"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Get the post text
    post_text = None
    
    if args.interactive:
        print("\n🎬 VidIn - LinkedIn Post to Video Generator")
        print("=" * 50)
        print("\nEnter your LinkedIn post text (press Enter twice to finish):\n")
        
        lines = []
        empty_count = 0
        while empty_count < 1:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        post_text = "\n".join(lines)
        
        print("\nSelect aspect ratio:")
        print("  1. 16:9 (YouTube, LinkedIn)")
        print("  2. 9:16 (TikTok, Reels, Shorts)")
        print("  3. 1:1 (Instagram Feed)")
        choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"
        
        ratio_map = {"1": "16:9", "2": "9:16", "3": "1:1"}
        args.ratio = ratio_map.get(choice, "16:9")
        
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            post_text = f.read()
    elif args.text:
        post_text = args.text
    else:
        parser.print_help()
        print("\n❌ Error: Please provide post text via -t, -f, or --interactive")
        sys.exit(1)
    
    if not post_text or not post_text.strip():
        print("❌ Error: Post text cannot be empty")
        sys.exit(1)
    
    # Generate the video
    try:
        output_path = generate_video_sync(
            linkedin_post=post_text,
            aspect_ratio=args.ratio,
            fps=args.fps,
            video_id=args.id
        )
        print(f"\n🎉 Done! Your video is ready at: {output_path}")
    except Exception as e:
        print(f"\n❌ Failed to generate video: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

