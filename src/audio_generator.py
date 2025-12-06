"""
Audio Generator Module
Generates voiceover audio with word-level timestamps using ElevenLabs API
"""

import os
import json
import subprocess
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import httpx


@dataclass
class WordTiming:
    """Represents timing information for a single word"""
    word: str
    start_time: float  # in seconds
    end_time: float    # in seconds


@dataclass
class SceneAudio:
    """Contains audio data and timing for a scene"""
    scene_number: int
    audio_path: str
    duration: float  # in seconds (including padding)
    original_duration: float  # duration without padding
    voiceover_text: str
    word_timings: List[WordTiming]


class AudioGenerator:
    """Generates audio from text using ElevenLabs API with word-level timestamps"""
    
    def __init__(self, temp_dir: str = "temp"):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def generate_scene_audio(
        self,
        scene_number: int,
        text: str,
        output_filename: Optional[str] = None,
        padding_seconds: float = 1.0
    ) -> SceneAudio:
        """
        Generate audio for a single scene with word-level timestamps
        
        Args:
            scene_number: The scene number
            text: The voiceover text
            output_filename: Optional custom filename
            padding_seconds: Silence to add at the end (default 1 second)
        
        Returns:
            SceneAudio object with audio path and timing data
        """
        if not output_filename:
            output_filename = f"scene_{scene_number}_audio.mp3"
        
        # Generate audio with timestamps using ElevenLabs
        audio_data, word_timings = self._generate_audio_with_timestamps(text)
        
        # Save the raw audio
        raw_audio_path = self.temp_dir / f"raw_{output_filename}"
        with open(raw_audio_path, "wb") as f:
            f.write(audio_data)
        
        # Get audio duration
        original_duration = self._get_audio_duration(str(raw_audio_path))
        
        # Add padding silence at the end
        final_audio_path = self.temp_dir / output_filename
        self._add_silence_padding(str(raw_audio_path), str(final_audio_path), padding_seconds)
        
        # Clean up raw audio
        raw_audio_path.unlink(missing_ok=True)
        
        # Calculate total duration with padding
        total_duration = original_duration + padding_seconds
        
        return SceneAudio(
            scene_number=scene_number,
            audio_path=str(final_audio_path),
            duration=total_duration,
            original_duration=original_duration,
            voiceover_text=text,
            word_timings=word_timings
        )
    
    def _generate_audio_with_timestamps(self, text: str) -> tuple:
        """
        Generate audio and get word-level timestamps from ElevenLabs
        
        Returns:
            Tuple of (audio_bytes, word_timings)
        """
        url = f"{self.base_url}/text-to-speech/{self.voice_id}/with-timestamps"
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=self.headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")
            
            result = response.json()
        
        # Extract audio bytes (base64 encoded)
        import base64
        audio_base64 = result.get("audio_base64", "")
        audio_bytes = base64.b64decode(audio_base64)
        
        # Extract word timings
        word_timings = []
        alignment = result.get("alignment", {})
        characters = alignment.get("characters", [])
        character_start_times = alignment.get("character_start_times_seconds", [])
        character_end_times = alignment.get("character_end_times_seconds", [])
        
        # Reconstruct words from characters
        if characters and character_start_times and character_end_times:
            word_timings = self._reconstruct_word_timings(
                characters, character_start_times, character_end_times
            )
        else:
            # Fallback: estimate word timings based on text
            word_timings = self._estimate_word_timings(text, 0.0)
        
        return audio_bytes, word_timings
    
    def _reconstruct_word_timings(
        self,
        characters: List[str],
        start_times: List[float],
        end_times: List[float]
    ) -> List[WordTiming]:
        """Reconstruct word timings from character-level data"""
        word_timings = []
        current_word = ""
        word_start = None
        word_end = None
        
        for i, char in enumerate(characters):
            if char == " " or i == len(characters) - 1:
                # Handle last character
                if i == len(characters) - 1 and char != " ":
                    current_word += char
                    word_end = end_times[i]
                
                # Save the word if we have one
                if current_word and word_start is not None:
                    word_timings.append(WordTiming(
                        word=current_word.strip(),
                        start_time=word_start,
                        end_time=word_end or start_times[i]
                    ))
                
                # Reset for next word
                current_word = ""
                word_start = None
                word_end = None
            else:
                if word_start is None:
                    word_start = start_times[i]
                current_word += char
                word_end = end_times[i]
        
        return word_timings
    
    def _estimate_word_timings(self, text: str, start_offset: float = 0.0) -> List[WordTiming]:
        """Fallback: Estimate word timings based on average speaking rate"""
        words = text.split()
        avg_word_duration = 0.4  # Average 150 WPM = ~0.4 seconds per word
        
        word_timings = []
        current_time = start_offset
        
        for word in words:
            # Adjust duration based on word length
            word_duration = max(0.2, len(word) * 0.05 + 0.15)
            
            word_timings.append(WordTiming(
                word=word,
                start_time=current_time,
                end_time=current_time + word_duration
            ))
            
            current_time += word_duration + 0.1  # Small gap between words
        
        return word_timings
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file using FFmpeg"""
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return float(result.stdout.strip())
        except (subprocess.CalledProcessError, ValueError):
            # Fallback: estimate based on file size (rough approximation)
            file_size = os.path.getsize(audio_path)
            # Approximate bitrate for MP3: 128kbps = 16KB/s
            return file_size / 16000
    
    def _add_silence_padding(self, input_path: str, output_path: str, padding_seconds: float):
        """Add silence padding to the end of an audio file using FFmpeg"""
        try:
            # Create silent audio segment
            silence_path = self.temp_dir / "silence.mp3"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"anullsrc=r=44100:cl=stereo",
                    "-t", str(padding_seconds),
                    "-q:a", "9",
                    "-acodec", "libmp3lame",
                    str(silence_path)
                ],
                capture_output=True,
                check=True
            )
            
            # Create a file list for concatenation
            list_path = self.temp_dir / "concat_list.txt"
            with open(list_path, "w") as f:
                f.write(f"file '{Path(input_path).resolve()}'\n")
                f.write(f"file '{silence_path.resolve()}'\n")
            
            # Concatenate audio with silence
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_path),
                    "-c", "copy",
                    output_path
                ],
                capture_output=True,
                check=True
            )
            
            # Clean up
            silence_path.unlink(missing_ok=True)
            list_path.unlink(missing_ok=True)
            
        except subprocess.CalledProcessError as e:
            # Fallback: just copy the file without padding
            import shutil
            shutil.copy(input_path, output_path)
            print(f"Warning: Could not add silence padding: {e}")
    
    def generate_all_scene_audio(
        self,
        scenes: List[Dict[str, Any]],
        padding_seconds: float = 1.0
    ) -> List[SceneAudio]:
        """
        Generate audio for all scenes
        
        Args:
            scenes: List of scene dictionaries with 'scene_number' and 'voiceover_text'
            padding_seconds: Silence to add at the end of each scene
        
        Returns:
            List of SceneAudio objects
        """
        scene_audios = []
        
        for scene in scenes:
            scene_number = scene.get("scene_number", len(scene_audios) + 1)
            voiceover_text = scene.get("voiceover_text", "")
            
            if not voiceover_text:
                continue
            
            print(f"Generating audio for scene {scene_number}...")
            
            scene_audio = self.generate_scene_audio(
                scene_number=scene_number,
                text=voiceover_text,
                padding_seconds=padding_seconds
            )
            
            scene_audios.append(scene_audio)
            print(f"  Duration: {scene_audio.duration:.2f}s (including {padding_seconds}s padding)")
        
        return scene_audios
    
    def merge_all_audio(self, scene_audios: List[SceneAudio], output_path: str) -> str:
        """
        Merge all scene audio files into a single audio file
        
        Args:
            scene_audios: List of SceneAudio objects
            output_path: Path for the final merged audio
        
        Returns:
            Path to the merged audio file
        """
        if not scene_audios:
            raise ValueError("No scene audios to merge")
        
        if len(scene_audios) == 1:
            import shutil
            shutil.copy(scene_audios[0].audio_path, output_path)
            return output_path
        
        # Create a file list for concatenation
        list_path = self.temp_dir / "merge_list.txt"
        with open(list_path, "w") as f:
            for sa in scene_audios:
                f.write(f"file '{Path(sa.audio_path).resolve()}'\n")
        
        # Merge audio files
        try:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(list_path),
                    "-c", "copy",
                    output_path
                ],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to merge audio files: {e}")
        finally:
            list_path.unlink(missing_ok=True)
        
        return output_path
    
    def get_subtitle_data_for_scene(self, scene_audio: SceneAudio, time_offset: float = 0.0) -> Dict[str, Any]:
        """
        Get subtitle data formatted for the video player
        
        Args:
            scene_audio: SceneAudio object
            time_offset: Time offset in seconds (for positioning in full video)
        
        Returns:
            Dictionary with subtitle data
        """
        words_data = []
        for wt in scene_audio.word_timings:
            words_data.append({
                "word": wt.word,
                "start": wt.start_time + time_offset,
                "end": wt.end_time + time_offset
            })
        
        return {
            "scene_number": scene_audio.scene_number,
            "text": scene_audio.voiceover_text,
            "start_time": time_offset,
            "end_time": time_offset + scene_audio.original_duration,
            "words": words_data
        }
    
    def cleanup(self, scene_audios: List[SceneAudio]):
        """Clean up temporary audio files"""
        for sa in scene_audios:
            try:
                Path(sa.audio_path).unlink(missing_ok=True)
            except:
                pass


if __name__ == "__main__":
    # Test the audio generator
    from dotenv import load_dotenv
    load_dotenv()
    
    test_text = "Hello, this is a test of the audio generation system with word-level timestamps."
    
    generator = AudioGenerator()
    scene_audio = generator.generate_scene_audio(
        scene_number=1,
        text=test_text,
        padding_seconds=1.0
    )
    
    print(f"Audio generated: {scene_audio.audio_path}")
    print(f"Duration: {scene_audio.duration:.2f}s")
    print(f"Word timings:")
    for wt in scene_audio.word_timings:
        print(f"  '{wt.word}': {wt.start_time:.2f}s - {wt.end_time:.2f}s")

