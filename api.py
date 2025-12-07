"""
VidIn FastAPI Backend

Provides REST API endpoints for video generation with real-time progress updates
via Server-Sent Events (SSE).
"""

import os
import sys
import json
import uuid
import asyncio
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase imports
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "vidin-videos")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import VidIn components
from src.script_generator import ScriptGenerator, VideoScript
from src.code_generator import CodeGenerator
from src.audio_generator import AudioGenerator, SceneAudio
from src.video_generator import VideoGenerator


# ============================================================================
# Request/Response Models
# ============================================================================

class VideoGenerationRequest(BaseModel):
    """Request body for video generation"""
    text: str
    aspectRatio: str = "16:9"


class VideoGenerationResponse(BaseModel):
    """Response after video generation is complete"""
    videoUrl: str
    jobId: str


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    jobId: str
    status: str  # 'pending', 'processing', 'complete', 'error'
    progress: int  # 0-100
    message: str
    videoUrl: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# Job Storage (In-Memory for simplicity - use Redis in production)
# ============================================================================

jobs: Dict[str, Dict[str, Any]] = {}

# Thread pool for running video generation (Playwright requires its own event loop on Windows)
executor = ThreadPoolExecutor(max_workers=2)


def update_job(job_id: str, status: str, progress: int, message: str, 
               video_url: str = None, error: str = None):
    """Update job status"""
    jobs[job_id] = {
        "status": status,
        "progress": progress,
        "message": message,
        "videoUrl": video_url,
        "error": error,
        "updatedAt": datetime.now().isoformat()
    }


# ============================================================================
# Video Generation with Progress Updates
# ============================================================================

class VidInWithProgress:
    """VidIn wrapper that reports progress updates"""
    
    VALID_ASPECT_RATIOS = ["1:1", "9:16", "16:9"]
    
    def __init__(self, job_id: str, temp_dir: str = "temp", output_dir: str = "videos"):
        self.job_id = job_id
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize generators
        self.script_generator = ScriptGenerator()
        self.code_generator = CodeGenerator()
        self.audio_generator = AudioGenerator(temp_dir=temp_dir)
        self.video_generator = VideoGenerator(temp_dir=temp_dir, output_dir=output_dir)
    
    def _update_progress(self, progress: int, message: str):
        """Update job progress"""
        update_job(self.job_id, "processing", progress, message)
    
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
        Generate a video from a LinkedIn post with progress updates
        """
        # Validate inputs
        aspect_ratio = self.validate_aspect_ratio(aspect_ratio)
        
        # Generate unique ID
        if not video_id:
            video_id = f"vidin_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Generate script (1% - 15%)
            self._update_progress(1, "Starting video generation...")
            self._update_progress(5, "Generating video script...")
            
            script = self.script_generator.generate_script(linkedin_post, aspect_ratio)
            self._update_progress(15, f"Script generated with {script.total_scenes} scenes")
            
            # Step 2: Generate animation code (15% - 25%)
            self._update_progress(20, "Creating animations...")
            html_code = self.code_generator.generate_code(script, aspect_ratio)
            self._update_progress(25, "Animation code generated")
            
            # Step 3: Generate audio for each scene (25% - 50%)
            self._update_progress(30, "Generating voiceover audio...")
            scenes_data = [
                {"scene_number": s.scene_number, "voiceover_text": s.voiceover_text}
                for s in script.scenes
            ]
            
            scene_audios = []
            total_scenes = len(scenes_data)
            for i, scene_data in enumerate(scenes_data):
                progress = 30 + int((i / total_scenes) * 20)
                self._update_progress(progress, f"Generating audio for scene {i + 1}/{total_scenes}...")
                
                scene_audio = self.audio_generator.generate_scene_audio(
                    scene_number=scene_data["scene_number"],
                    text=scene_data["voiceover_text"],
                    padding_seconds=1.0
                )
                scene_audios.append(scene_audio)
            
            self._update_progress(50, "Audio generation complete")
            
            # Calculate scene durations and subtitle data
            scene_durations = [sa.duration for sa in scene_audios]
            total_duration = sum(scene_durations)
            
            # Build subtitle data with proper time offsets
            subtitle_data = []
            time_offset = 0.0
            for sa in scene_audios:
                subtitle_info = self.audio_generator.get_subtitle_data_for_scene(sa, time_offset)
                subtitle_data.append(subtitle_info)
                time_offset += sa.duration
            
            # Step 4: Update HTML with timing data (50% - 55%)
            self._update_progress(52, "Synchronizing timing data...")
            html_code = self.code_generator.update_html_with_timing(
                html_code, scene_durations, subtitle_data
            )
            
            # Save HTML file
            html_path = self.temp_dir / f"{video_id}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_code)
            
            # Merge all audio files
            merged_audio_path = self.temp_dir / f"{video_id}_merged.mp3"
            self.audio_generator.merge_all_audio(scene_audios, str(merged_audio_path))
            self._update_progress(55, "Audio merged")
            
            # Step 5: Render video (55% - 95%)
            self._update_progress(60, "Rendering video frames...")
            
            # Create a progress callback for the video renderer
            def render_progress_callback(progress: int, message: str):
                self._update_progress(progress, message)
            
            output_path = await self.video_generator.render_video(
                html_path=str(html_path),
                audio_path=str(merged_audio_path),
                scene_durations=scene_durations,
                subtitle_data=subtitle_data,
                aspect_ratio=aspect_ratio,
                fps=fps,
                video_id=video_id,
                progress_callback=render_progress_callback
            )
            
            self._update_progress(95, "Video rendering complete")
            
            # Step 6: Upload to Supabase (95% - 100%)
            video_url = output_path
            
            if supabase:
                self._update_progress(97, "Uploading to cloud storage...")
                video_url = await self._upload_to_supabase(output_path, video_id)
                self._update_progress(99, "Upload complete")
            
            # Cleanup temporary files
            self._cleanup(video_id, scene_audios, html_path, merged_audio_path)
            
            # Update final status
            update_job(self.job_id, "complete", 100, "Video generated successfully!", video_url)
            
            return video_url
            
        except Exception as e:
            error_msg = str(e)
            update_job(self.job_id, "error", 0, "Video generation failed", error=error_msg)
            raise
    
    async def _upload_to_supabase(self, local_path: str, video_id: str) -> str:
        """Upload video to Supabase storage and return public URL"""
        if not supabase:
            return local_path
        
        try:
            file_path = f"{video_id}.mp4"
            
            with open(local_path, "rb") as f:
                video_data = f.read()
            
            # Upload to Supabase storage
            result = supabase.storage.from_(SUPABASE_BUCKET).upload(
                file_path,
                video_data,
                {"content-type": "video/mp4"}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
            
            return public_url
            
        except Exception as e:
            print(f"Failed to upload to Supabase: {e}")
            # Return local path as fallback
            return local_path
    
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


def run_video_generation_sync(job_id: str, text: str, aspect_ratio: str):
    """
    Synchronous wrapper to run video generation in a separate thread.
    
    This is needed because Playwright on Windows doesn't work well with
    nested event loops (like when running inside uvicorn).
    """
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        vidin = VidInWithProgress(job_id)
        loop.run_until_complete(vidin.generate_video(text, aspect_ratio))
    except Exception as e:
        update_job(job_id, "error", 0, "Video generation failed", error=str(e))
    finally:
        loop.close()


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 VidIn API starting up...")
    yield
    # Shutdown
    print("👋 VidIn API shutting down...")
    executor.shutdown(wait=False)


app = FastAPI(
    title="VidIn API",
    description="Transform LinkedIn posts into engaging videos",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - only allow specific frontend origins
allowed_origins = [
    # Production frontend
    "https://vidin-frontend.vercel.app",
    # Local development
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Add FRONTEND_URL from environment if set (for custom domains)
frontend_url = os.getenv("FRONTEND_URL", "")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "VidIn API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/generate", response_model=JobStatusResponse)
async def generate_video(request: VideoGenerationRequest):
    """
    Start video generation job.
    
    Returns a job ID that can be used to check progress via the /progress/{job_id} endpoint.
    """
    # Validate input
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text content is required")
    
    if request.aspectRatio not in ["1:1", "9:16", "16:9"]:
        raise HTTPException(status_code=400, detail="Invalid aspect ratio")
    
    # Limit text length to prevent very long videos that exceed server resources
    max_text_length = 1500  # ~200-250 words, produces ~45-60 second videos
    if len(request.text.strip()) > max_text_length:
        raise HTTPException(
            status_code=400, 
            detail=f"Text is too long ({len(request.text)} chars). Maximum is {max_text_length} characters to ensure video generation completes successfully."
        )
    
    # Create job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    update_job(job_id, "pending", 0, "Job queued")
    
    # Submit video generation to thread pool
    # This runs in a separate thread with its own event loop to avoid
    # Windows asyncio subprocess issues with Playwright
    executor.submit(
        run_video_generation_sync,
        job_id,
        request.text,
        request.aspectRatio
    )
    
    return JobStatusResponse(
        jobId=job_id,
        status="pending",
        progress=0,
        message="Video generation started"
    )


@app.get("/progress/{job_id}")
async def get_progress_sse(job_id: str):
    """
    Server-Sent Events endpoint for real-time progress updates.
    
    Connect to this endpoint to receive progress updates as the video is being generated.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        last_progress = -1
        
        while True:
            if job_id not in jobs:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            
            job = jobs[job_id]
            current_progress = job.get("progress", 0)
            
            # Send update if progress changed
            if current_progress != last_progress:
                data = {
                    "jobId": job_id,
                    "status": job.get("status", "unknown"),
                    "progress": current_progress,
                    "message": job.get("message", ""),
                    "videoUrl": job.get("videoUrl"),
                    "error": job.get("error")
                }
                yield f"data: {json.dumps(data)}\n\n"
                last_progress = current_progress
            
            # Check if job is complete or errored
            if job.get("status") in ["complete", "error"]:
                break
            
            await asyncio.sleep(0.5)  # Poll every 500ms
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get current status of a video generation job.
    
    Use this for polling-based progress updates if SSE is not available.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    return JobStatusResponse(
        jobId=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        message=job.get("message", ""),
        videoUrl=job.get("videoUrl"),
        error=job.get("error")
    )


# ============================================================================
# Run with Uvicorn
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
