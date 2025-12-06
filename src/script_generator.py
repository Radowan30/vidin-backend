"""
Script Generator Module
Generates detailed scene-by-scene scripts from LinkedIn posts using Groq API
"""

import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from groq import Groq


class SceneAnimation(BaseModel):
    """Describes an animation element within a scene"""
    element_type: str = Field(description="Type of element: 'icon', 'chart', 'text', 'shape', 'illustration', 'infographic', 'list', 'image', 'badge', 'progress', 'button', 'card', 'avatar', 'video', 'logo', 'slider', 'diagram', 'arrow', 'counter', 'timeline', 'grid', 'quote', 'code'")
    description: str = Field(description="Detailed description of the visual element")
    animation_type: str = Field(description="Type of animation: 'fade_in', 'slide_in', 'scale_up', 'bounce', 'draw', 'morph', 'pulse', 'rotate', 'float', 'typewriter', 'wipe', 'flip', 'shake', 'glow', 'stagger', 'zoom', 'spin', 'wave', 'pop', 'highlight', 'reveal', 'expand', 'shrink', 'swing', 'flash', 'grow'")
    animation_direction: Optional[str] = Field(default="center", description="Direction: 'left', 'right', 'top', 'bottom', 'center'")
    color_scheme: Optional[str] = Field(default=None, description="Primary colors to use, e.g., '#3B82F6, #10B981'")
    position: str = Field(description="Position on screen: 'center', 'top', 'bottom', 'left', 'right', 'top-left', 'top-right', 'top-center', 'bottom-left', 'bottom-right', 'bottom-center', 'center-left', 'center-right', 'center-top', 'center-bottom', 'left-center', 'right-center', 'background', 'full', 'overlay'")
    size: str = Field(default="medium", description="Size: 'small', 'medium', 'large', 'full'")


class Scene(BaseModel):
    """Represents a single scene in the video"""
    scene_number: int = Field(description="Sequential scene number starting from 1")
    scene_title: str = Field(description="Brief title describing the scene's purpose")
    duration_suggestion: float = Field(description="Suggested duration in seconds (will be adjusted based on audio)")
    voiceover_text: str = Field(description="The text to be spoken during this scene")
    visual_description: str = Field(description="Overall visual description of what's happening in the scene")
    background_style: str = Field(description="Background style: 'gradient', 'solid', 'pattern', 'animated'")
    background_colors: str = Field(description="Background colors, e.g., '#1a1a2e, #16213e' for gradient")
    animations: List[SceneAnimation] = Field(description="List of animated elements in the scene")
    transition_in: str = Field(default="fade", description="Transition effect entering scene: 'fade', 'slide', 'zoom', 'wipe'")
    transition_out: str = Field(default="fade", description="Transition effect leaving scene: 'fade', 'slide', 'zoom', 'wipe'")


class VideoScript(BaseModel):
    """Complete video script with all scenes"""
    title: str = Field(description="Title of the video")
    total_scenes: int = Field(description="Total number of scenes")
    theme: str = Field(description="Overall visual theme: 'professional', 'creative', 'minimal', 'bold', 'tech', 'corporate'")
    primary_color: str = Field(description="Primary brand color in hex")
    secondary_color: str = Field(description="Secondary accent color in hex")
    font_style: str = Field(description="Font style: 'modern', 'classic', 'playful', 'tech', 'elegant'")
    scenes: List[Scene] = Field(description="List of all scenes in order")


class ScriptGenerator:
    """Generates video scripts from LinkedIn posts using Groq API"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
    
    def _get_aspect_ratio_context(self, aspect_ratio: str) -> str:
        """Returns context about the aspect ratio for the LLM"""
        contexts = {
            "1:1": "Square format (1080x1080), ideal for Instagram feed. Content should be centered and balanced. Use larger text and elements since space is compact.",
            "9:16": "Vertical/Portrait format (1080x1920), ideal for TikTok, Instagram Reels, YouTube Shorts. Stack elements vertically. Great for mobile viewing. Use the full vertical space creatively.",
            "16:9": "Horizontal/Landscape format (1920x1080), ideal for YouTube, LinkedIn video. Wide format allows side-by-side elements. Traditional presentation style."
        }
        return contexts.get(aspect_ratio, contexts["16:9"])
    
    def _get_dimensions(self, aspect_ratio: str) -> tuple:
        """Returns width, height for the aspect ratio"""
        dimensions = {
            "1:1": (1080, 1080),
            "9:16": (1080, 1920),
            "16:9": (1920, 1080)
        }
        return dimensions.get(aspect_ratio, (1920, 1080))
    
    def generate_script(self, linkedin_post: str, aspect_ratio: str = "16:9") -> VideoScript:
        """
        Generate a detailed video script from a LinkedIn post
        
        Args:
            linkedin_post: The text content of the LinkedIn post
            aspect_ratio: Video aspect ratio ("1:1", "9:16", "16:9")
        
        Returns:
            VideoScript object containing all scene details
        """
        aspect_context = self._get_aspect_ratio_context(aspect_ratio)
        width, height = self._get_dimensions(aspect_ratio)
        
        system_prompt = f"""You are an expert video content creator and motion graphics designer. Your task is to transform LinkedIn posts into engaging, animated video scripts.

ASPECT RATIO CONTEXT:
{aspect_context}
Dimensions: {width}x{height} pixels

CRITICAL REQUIREMENTS:
1. EVERY scene MUST have movement and animation - static content is NOT allowed
2. Create 3-6 scenes depending on content length
3. Each scene should have 3-5 animated elements minimum
4. Voiceover text should be conversational and engaging
5. Use modern, professional color schemes
6. Animations should be smooth and purposeful, not distracting
7. Include data visualizations (charts, graphs, icons) where relevant
8. Text animations should highlight key points
9. Each scene's voiceover should be 5-15 seconds when spoken

KEY CONCEPT VISUALIZATION (VERY IMPORTANT):
- For EVERY key concept/term mentioned in the voiceover, create a corresponding animated icon or visual
- Example: If voiceover mentions "TOTP backup codes, hardware key support, and SMS", create 3 separate icons:
  * One icon for TOTP (e.g., phone with code)
  * One icon for hardware key (e.g., USB key icon)
  * One icon for SMS (e.g., message bubble icon)
- Each concept icon should appear with staggered timing (one after another)
- Icons should have continuous floating/hovering animation after appearing
- Position icons in a row or grid layout so they're all visible together

ANIMATION GUIDELINES:
- Icons should float, hover, or pulse continuously after appearing (3D-like movement)
- Use staggered animations - each icon appears 0.3-0.5s after the previous
- Text should fade in with slide effects
- Charts/graphs should draw themselves progressively
- Use scale_up + float for 3D-like icon entrances
- Always have multiple things moving to keep viewer attention

AVAILABLE ANIMATION TYPES (use ONLY these):
- fade_in: Element fades in from transparent
- slide_in: Element slides in from a direction
- scale_up: Element grows from small to full size
- bounce: Element bounces into place
- draw: Element draws itself (great for charts/lines)
- morph: Element morphs/transforms shape
- pulse: Element pulses/throbs continuously
- rotate: Element rotates into place
- float: Element floats up and down gently
- typewriter: Text appears letter by letter
- wipe: Element wipes in from a direction
- flip: Element flips into view
- shake: Element shakes for emphasis
- glow: Element glows/brightens

AVAILABLE POSITIONS (use ONLY these):
- center: Center of screen
- top: Top edge center
- bottom: Bottom edge center
- left: Left edge center
- right: Right edge center
- top-left: Top left corner
- top-right: Top right corner
- top-center: Top center
- bottom-left: Bottom left corner
- bottom-right: Bottom right corner
- bottom-center: Bottom center
- center-left: Center left
- center-right: Center right
- center-top: Same as top-center
- center-bottom: Same as bottom-center

VISUAL STYLE GUIDELINES:
- Use gradients for modern feel
- Incorporate geometric shapes as decorative elements
- Icons should be simple, line-style or filled modern icons
- Use shadows and depth for hierarchy
- Ensure high contrast for readability

OUTPUT: Generate a complete video script with detailed scene descriptions, animations, and voiceover text. Make it visually interesting and engaging."""

        user_prompt = f"""Transform this LinkedIn post into an engaging animated video script:

---
{linkedin_post}
---

Create a detailed scene-by-scene breakdown with:
1. Compelling voiceover text (conversational, not just reading the post)
2. Specific animated visual elements for each scene
3. Color schemes that work well together
4. Animation types that enhance the message
5. Proper transitions between scenes

Remember: Every element must animate! The video should be dynamic and engaging to watch."""

        # Define the JSON schema for structured output
        json_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "total_scenes": {"type": "integer"},
                "theme": {"type": "string", "enum": ["professional", "creative", "minimal", "bold", "tech", "corporate"]},
                "primary_color": {"type": "string"},
                "secondary_color": {"type": "string"},
                "font_style": {"type": "string", "enum": ["modern", "classic", "playful", "tech", "elegant"]},
                "scenes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "scene_number": {"type": "integer"},
                            "scene_title": {"type": "string"},
                            "duration_suggestion": {"type": "number"},
                            "voiceover_text": {"type": "string"},
                            "visual_description": {"type": "string"},
                            "background_style": {"type": "string", "enum": ["gradient", "solid", "pattern", "animated"]},
                            "background_colors": {"type": "string"},
                            "animations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "element_type": {"type": "string", "enum": ["icon", "chart", "text", "shape", "illustration", "infographic", "list", "image", "badge", "progress", "button", "card", "avatar", "video", "logo", "slider", "diagram", "arrow", "counter", "timeline", "grid", "quote", "code"]},
                                        "description": {"type": "string"},
                                        "animation_type": {"type": "string", "enum": ["fade_in", "slide_in", "scale_up", "bounce", "draw", "morph", "pulse", "rotate", "float", "typewriter", "wipe", "flip", "shake", "glow", "stagger", "zoom", "spin", "wave", "pop", "highlight", "reveal", "expand", "shrink", "swing", "flash", "grow"]},
                                        "animation_direction": {"type": "string", "enum": ["left", "right", "top", "bottom", "center"]},
                                        "color_scheme": {"type": "string"},
                                        "position": {"type": "string", "enum": ["center", "top", "bottom", "left", "right", "top-left", "top-right", "top-center", "bottom-left", "bottom-right", "bottom-center", "center-left", "center-right", "center-top", "center-bottom", "left-center", "right-center", "background", "full", "overlay", "random", "scattered", "around", "behind", "front", "sides"]},
                                        "size": {"type": "string", "enum": ["small", "medium", "large", "full"]}
                                    },
                                    "required": ["element_type", "description", "animation_type", "position"]
                                }
                            },
                            "transition_in": {"type": "string", "enum": ["fade", "slide", "zoom", "wipe"]},
                            "transition_out": {"type": "string", "enum": ["fade", "slide", "zoom", "wipe", "none"]}
                        },
                        "required": ["scene_number", "scene_title", "duration_suggestion", "voiceover_text", "visual_description", "background_style", "background_colors", "animations"]
                    }
                }
            },
            "required": ["title", "total_scenes", "theme", "primary_color", "secondary_color", "font_style", "scenes"]
        }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "video_script",
                    "schema": json_schema,
                    "strict": True
                }
            },
            temperature=0.7,
            max_tokens=4096
        )
        
        # Parse the response
        script_data = json.loads(response.choices[0].message.content)
        
        # Convert to Pydantic model for validation
        video_script = VideoScript(**script_data)
        
        return video_script


if __name__ == "__main__":
    # Test the script generator
    from dotenv import load_dotenv
    load_dotenv()
    
    test_post = """
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
    
    generator = ScriptGenerator()
    script = generator.generate_script(test_post, "16:9")
    print(json.dumps(script.model_dump(), indent=2))

