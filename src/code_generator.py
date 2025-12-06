"""
Code Generator Module
Generates HTML/JS animation code from video scripts using VidIn Animation Library
Uses Anime.js with pre-built professional animation sequences
"""

import os
import json
from typing import List, Dict, Any
from groq import Groq
from .script_generator import VideoScript, Scene


class CodeGenerator:
    """Generates animation code from video scripts using VidIn Animation Library"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        
        # Load animation library
        self.animation_library = self._load_animation_library()
    
    def _load_animation_library(self) -> str:
        """Load the animation library JS file"""
        lib_path = os.path.join(os.path.dirname(__file__), 'animation-library.js')
        try:
            with open(lib_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "// animation-library.js not found"
    
    def _get_dimensions(self, aspect_ratio: str) -> tuple:
        """Returns width, height for the aspect ratio"""
        dimensions = {
            "1:1": (1080, 1080),
            "9:16": (1080, 1920),
            "16:9": (1920, 1080)
        }
        return dimensions.get(aspect_ratio, (1920, 1080))
    
    def _create_base_template(self, aspect_ratio: str, script: VideoScript) -> str:
        """Creates the base HTML template with animation library"""
        width, height = self._get_dimensions(aspect_ratio)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{script.title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.0.0/fonts/remixicon.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: 'Inter', 'Poppins', sans-serif;
            background: #0a0a0a;
        }}
        
        #video-container {{
            width: {width}px;
            height: {height}px;
            position: relative;
            overflow: hidden;
        }}
        
        .scene {{
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: {width}px !important;
            height: {height}px !important;
            opacity: 0;
            visibility: hidden;
            overflow: hidden;
        }}
        
        .scene.active {{
            opacity: 1;
            visibility: visible;
        }}
        
        /* Subtitle container */
        #subtitle-container {{
            position: fixed;
            bottom: {int(height * 0.06)}px;
            left: 50%;
            transform: translateX(-50%);
            width: 90%;
            text-align: center;
            z-index: 1000;
            pointer-events: none;
        }}
        
        #subtitle-text {{
            font-family: 'Poppins', sans-serif;
            font-size: {max(26, int(height * 0.026))}px;
            font-weight: 600;
            color: #ffffff;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.9), 0 0 30px rgba(0,0,0,0.7);
            line-height: 1.4;
            padding: 12px 24px;
            background: rgba(0, 0, 0, 0.65);
            border-radius: 10px;
            backdrop-filter: blur(10px);
            display: inline-block;
        }}
        
        #subtitle-text .word {{
            display: inline;
            transition: color 0.05s ease;
        }}
        
        #subtitle-text .word.highlight {{
            color: #FFD700;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.9), 0 0 40px rgba(255,215,0,0.6);
        }}
    </style>
</head>
<body>
    <div id="video-container">
        __SCENES_HTML_PLACEHOLDER__
        
        <div id="subtitle-container">
            <div id="subtitle-text"></div>
        </div>
    </div>
    
    <script>
        // VidIn Animation Library
        {self.animation_library}
    </script>
    
    <script>
        // Scene data and timelines
        let sceneDurations = __SCENE_DURATIONS_PLACEHOLDER__;
        let subtitleData = __SUBTITLE_DATA_PLACEHOLDER__;
        let sceneTimelines = [];
        let currentSceneIndex = -1;
        let currentTime = 0;
        
        // Video dimensions
        const VIDEO_WIDTH = {width};
        const VIDEO_HEIGHT = {height};
        
        // Initialize all scene animations
        function initializeScenes() {{
            __SCENE_INIT_CODE__
        }}
        
        // Switch to a specific scene
        function switchToScene(sceneIndex) {{
            const scenes = document.querySelectorAll('.scene');
            scenes.forEach((scene, index) => {{
                if (index === sceneIndex) {{
                    scene.classList.add('active');
                    scene.style.opacity = 1;
                    scene.style.visibility = 'visible';
                }} else {{
                    scene.classList.remove('active');
                    scene.style.opacity = 0;
                    scene.style.visibility = 'hidden';
                }}
            }});
            currentSceneIndex = sceneIndex;
        }}
        
        // Update subtitle with word highlighting
        function updateSubtitle(text, highlightIndex = -1) {{
            const container = document.getElementById('subtitle-text');
            if (!text) {{
                container.innerHTML = '';
                return;
            }}
            
            const words = text.split(' ');
            container.innerHTML = words.map((word, index) => {{
                const isHighlighted = index === highlightIndex;
                return `<span class="word${{isHighlighted ? ' highlight' : ''}}">${{word}} </span>`;
            }}).join('');
        }}
        
        // Clear subtitle
        function clearSubtitle() {{
            document.getElementById('subtitle-text').innerHTML = '';
        }}
        
        // Get total duration
        function getTotalDuration() {{
            return sceneDurations.reduce((sum, d) => sum + d, 0);
        }}
        
        // Get scene at time
        function getSceneAtTime(globalTime) {{
            let accumulated = 0;
            for (let i = 0; i < sceneDurations.length; i++) {{
                if (globalTime < accumulated + sceneDurations[i]) {{
                    return {{ sceneIndex: i, localTime: globalTime - accumulated }};
                }}
                accumulated += sceneDurations[i];
            }}
            return {{ sceneIndex: sceneDurations.length - 1, localTime: 0 }};
        }}
        
        // Seek to specific time
        function seekToTime(time) {{
            currentTime = time;
            const {{ sceneIndex, localTime }} = getSceneAtTime(time);
            
            // Switch scene if needed
            if (sceneIndex !== currentSceneIndex) {{
                switchToScene(sceneIndex);
            }}
            
            // Seek timeline for this scene
            if (sceneTimelines[sceneIndex]) {{
                sceneTimelines[sceneIndex].seek(localTime * 1000); // Anime.js uses ms
            }}
        }}
        
        // Build master timeline
        function buildMasterTimeline() {{
            initializeScenes();
            currentTime = 0;
            currentSceneIndex = -1;
            return true;
        }}
        
        // Start video
        function startVideo() {{
            buildMasterTimeline();
            seekToTime(0);
        }}
        
        // Control functions for Playwright
        window.videoController = {{
            play: () => {{}},
            pause: () => {{}},
            seek: (time) => seekToTime(time),
            getTime: () => currentTime,
            getDuration: () => getTotalDuration(),
            isComplete: () => currentTime >= getTotalDuration(),
            switchScene: switchToScene,
            updateSubtitle: updateSubtitle,
            clearSubtitle: clearSubtitle,
            setSceneDurations: (durations) => {{ sceneDurations = durations; }},
            setSubtitleData: (data) => {{ subtitleData = data; }},
            rebuild: buildMasterTimeline,
            start: startVideo
        }};
    </script>
</body>
</html>'''

    def generate_code(self, script: VideoScript, aspect_ratio: str = "16:9") -> str:
        """Generate HTML/JS animation code from a video script"""
        width, height = self._get_dimensions(aspect_ratio)
        
        # Generate scene HTML containers
        scenes_html = []
        scene_init_code = []
        used_functions = []  # Track which functions have been used for variety
        
        for i, scene in enumerate(script.scenes):
            # Create empty scene container
            scene_html = f'<div class="scene" id="scene-{i + 1}"></div>'
            scenes_html.append(scene_html)
            
            # Generate the VidIn function call for this scene (passing used functions for variety)
            init_code, func_name = self._generate_scene_init(scene, script, i, used_functions)
            scene_init_code.append(init_code)
            if func_name:
                used_functions.append(func_name)
        
        # Create the complete HTML
        template = self._create_base_template(aspect_ratio, script)
        
        # Replace placeholders
        html_content = template.replace("__SCENES_HTML_PLACEHOLDER__", "\n        ".join(scenes_html))
        html_content = html_content.replace("__SCENE_INIT_CODE__", "\n            ".join(scene_init_code))
        html_content = html_content.replace("__SUBTITLE_DATA_PLACEHOLDER__", "[]")
        html_content = html_content.replace("__SCENE_DURATIONS_PLACEHOLDER__", 
            "/*DURATIONS*/" + json.dumps([s.duration_suggestion for s in script.scenes]) + "/*END*/")
        
        return html_content
    
    def _generate_scene_init(self, scene: Scene, script: VideoScript, index: int, used_functions: List[str] = None) -> tuple:
        """Generate VidIn animation function call for a scene
        
        Returns:
            tuple: (init_code, function_name)
        """
        sn = index + 1
        
        # Analyze the scene to determine which animation to use (passing used functions for variety)
        function_call = self._select_animation_function(scene, script, used_functions or [])
        
        # Extract function name for tracking
        func_name = None
        if function_call.startswith('VidIn.'):
            func_name = function_call.split('(')[0].replace('VidIn.', '')
        
        init_code = f'''// Scene {sn}: {scene.scene_title}
            (function() {{
                try {{
                    const container = document.getElementById('scene-{sn}');
                    if (!container) {{
                        console.error('Scene container scene-{sn} not found');
                        return;
                    }}
                    const tl = {function_call};
                    if (tl) sceneTimelines[{index}] = tl;
                }} catch (e) {{
                    console.error('Error initializing scene {sn}:', e);
                }}
            }})();'''
        
        return init_code, func_name
    
    def _select_animation_function(self, scene: Scene, script: VideoScript, used_functions: List[str] = None) -> str:
        """Use LLM to select the appropriate animation function and parameters"""
        
        pc = script.primary_color
        sc = script.secondary_color
        
        # Dark background colors - rotate through these for variety
        dark_backgrounds = [
            '#0f0f1a',  # Deep navy
            '#1a1a2e',  # Dark purple-navy  
            '#16213e',  # Dark blue
            '#0d1b2a',  # Dark teal-blue
            '#1b2838',  # Steam dark
            '#2d132c',  # Dark purple
            '#0a192f',  # Terminal dark
            '#1f1f2e',  # Soft dark
        ]
        bg_color = dark_backgrounds[scene.scene_number % len(dark_backgrounds)]
        
        # Build avoid list for variety
        avoid_hint = ""
        if used_functions and len(used_functions) > 0:
            avoid_hint = f"\n\nIMPORTANT - DO NOT USE THESE (already used in previous scenes): {', '.join(used_functions[-3:])}"
            avoid_hint += "\nChoose a DIFFERENT animation function for variety!"
        
        system_prompt = f"""You select VidIn animation functions for video scenes. Return ONLY a JavaScript function call.

CRITICAL REQUIREMENTS:
1. ALWAYS use bgColor: "{bg_color}" (dark background)
2. Text colors should be light (#fff or rgba(255,255,255,0.8))
3. Analyze voiceover and create icons for EACH key concept mentioned
4. VARY animations - each scene should use a DIFFERENT function from previous scenes{avoid_hint}

AVAILABLE FUNCTIONS (choose different ones for each scene!):

1. VidIn.heroTitleReveal(container, {{ title, subtitle, icon, primaryColor, secondaryColor, bgColor }})
   - Opening scenes, big announcements

2. VidIn.conceptShowcase(container, {{ concepts, title, primaryColor, secondaryColor, bgColor }})
   - 2-5 key concepts with 3D floating cards
   - concepts: array of {{ icon, label, description }}
   - BEST for scenes listing technologies/methods/features

3. VidIn.iconGridReveal(container, {{ items, columns, title, primaryColor, secondaryColor, bgColor }})
   - Grid of concept icons, items: array of {{ icon, label }}

4. VidIn.bulletPointList(container, {{ title, items, icons, primaryColor, secondaryColor, bgColor }})
   - List with icons, items: array of strings, icons: array of icon names

5. VidIn.statisticShowcase(container, {{ number, suffix, label, icon, color, bgColor }})
   - Single big statistic with counter animation

6. VidIn.beforeAfterComparison(container, {{ beforeValue, afterValue, unit, label, beforeColor, afterColor, bgColor }})
   - Compare two values with bars

7. VidIn.multiStatReveal(container, {{ stats, title, primaryColor, secondaryColor, bgColor }})
   - Multiple stats: array of {{ value, suffix, label, icon }}

8. VidIn.impactMetrics(container, {{ metrics, title, primaryColor, secondaryColor, bgColor }})
   - 3 impact metrics: array of {{ icon, value, suffix, label }}

9. VidIn.processFlow(container, {{ steps, primaryColor, secondaryColor, bgColor }})
   - Sequential steps/workflow

10. VidIn.callToAction(container, {{ question, subtext, icon, primaryColor, secondaryColor, bgColor }})
    - Ending scenes, engagement prompts

11. VidIn.keyTakeaway(container, {{ takeaway, icon, primaryColor, secondaryColor, bgColor }})
    - Single important message/conclusion

12. VidIn.quoteReveal(container, {{ quote, author, primaryColor, secondaryColor, bgColor }})
    - Key statements, quotes

13. VidIn.celebrationFinale(container, {{ title, subtitle, primaryColor, secondaryColor, bgColor }})
    - Final celebration scene

ICONS: ri-lock-fill, ri-shield-fill, ri-key-fill, ri-database-2-fill, ri-server-fill, 
ri-code-s-slash-fill, ri-rocket-fill, ri-speed-fill, ri-check-double-fill, ri-trophy-fill,
ri-lightbulb-flash-fill, ri-bar-chart-box-fill, ri-user-fill, ri-message-3-fill, ri-smartphone-fill,
ri-money-dollar-circle-fill, ri-time-fill, ri-settings-fill, ri-star-fill, ri-heart-fill

Return ONLY the function call with bgColor: "{bg_color}" included."""

        user_prompt = f"""Scene {scene.scene_number} of {len(script.scenes)}:

Title: {scene.scene_title}
Voiceover: "{scene.voiceover_text}"
Visual: {scene.visual_description}
Colors: primary={pc}, secondary={sc}

Return the VidIn function call. Use bgColor: "{bg_color}". Extract key concepts from voiceover for icons."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            function_call = response.choices[0].message.content.strip()
            
            # Clean up response
            if function_call.startswith("```"):
                lines = function_call.split('\n')
                function_call = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
            function_call = function_call.strip()
            
            # Validate it starts with VidIn.
            if not function_call.startswith('VidIn.'):
                return self._get_fallback_function(scene, script, used_functions)
            
            return function_call
            
        except Exception as e:
            print(f"    ⚠ Using fallback for scene {scene.scene_number}: {str(e)[:50]}...")
            return self._get_fallback_function(scene, script, used_functions)
    
    def _get_fallback_function(self, scene: Scene, script: VideoScript, used_functions: List[str] = None) -> str:
        """Get a fallback animation function based on scene number, ensuring variety"""
        pc = script.primary_color
        sc = script.secondary_color
        sn = scene.scene_number
        total = len(script.scenes)
        
        title = self._escape_js(scene.scene_title)
        
        # Dark backgrounds - rotate through for variety
        dark_bgs = ['#0f0f1a', '#1a1a2e', '#16213e', '#0d1b2a', '#1b2838', '#2d132c', '#0a192f', '#1f1f2e']
        bg = dark_bgs[sn % len(dark_bgs)]
        
        # All available fallback functions with variety
        fallback_options = [
            ('heroTitleReveal', f"VidIn.heroTitleReveal(container, {{ title: \"{title}\", subtitle: \"Let's explore\", icon: \"ri-rocket-fill\", primaryColor: \"{pc}\", secondaryColor: \"{sc}\", bgColor: \"{bg}\" }})"),
            ('conceptShowcase', f'VidIn.conceptShowcase(container, {{ title: "{title}", concepts: [{{icon: "ri-lightbulb-flash-fill", label: "Key Idea"}}, {{icon: "ri-settings-fill", label: "Method"}}, {{icon: "ri-code-s-slash-fill", label: "Result"}}], primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('statisticShowcase', f'VidIn.statisticShowcase(container, {{ number: 73, suffix: "%", label: "Improvement", icon: "ri-speed-fill", color: "{pc}", bgColor: "{bg}" }})'),
            ('bulletPointList', f'VidIn.bulletPointList(container, {{ title: "{title}", items: ["First key point", "Second key point", "Third key point"], icons: ["ri-check-double-fill", "ri-star-fill", "ri-trophy-fill"], primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('iconGridReveal', f'VidIn.iconGridReveal(container, {{ title: "{title}", items: [{{icon: "ri-shield-fill", label: "Security"}}, {{icon: "ri-speed-fill", label: "Speed"}}, {{icon: "ri-database-2-fill", label: "Data"}}, {{icon: "ri-code-s-slash-fill", label: "Code"}}], columns: 2, primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('keyTakeaway', f'VidIn.keyTakeaway(container, {{ takeaway: "{title}", icon: "ri-lightbulb-flash-fill", primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('impactMetrics', f'VidIn.impactMetrics(container, {{ title: "{title}", metrics: [{{icon: "ri-user-fill", value: 95, suffix: "%", label: "Users"}}, {{icon: "ri-speed-fill", value: 73, suffix: "%", label: "Faster"}}, {{icon: "ri-money-dollar-circle-fill", value: 40, suffix: "%", label: "Savings"}}], primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('processFlow', f'VidIn.processFlow(container, {{ steps: ["Step 1", "Step 2", "Step 3"], primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('callToAction', f'VidIn.callToAction(container, {{ question: "{title}", subtext: "Share your thoughts!", icon: "ri-chat-smile-3-fill", primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
            ('quoteReveal', f'VidIn.quoteReveal(container, {{ quote: "{title}", author: "The Key Insight", primaryColor: "{pc}", secondaryColor: "{sc}", bgColor: "{bg}" }})'),
        ]
        
        used = used_functions or []
        
        # First scene: heroTitleReveal
        if sn == 1:
            return fallback_options[0][1]
        # Last scene: callToAction
        elif sn == total:
            return fallback_options[8][1]
        else:
            # Find an option not recently used
            for name, func in fallback_options:
                if name not in used[-3:]:  # Avoid last 3 used functions
                    return func
            # If all used, pick based on scene number
            return fallback_options[sn % len(fallback_options)][1]
    
    def _escape_js(self, text: str) -> str:
        """Escape text for JavaScript strings"""
        return text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
    
    def update_html_with_timing(self, html_content: str, scene_durations: List[float], subtitle_data: List[Dict[str, Any]]) -> str:
        """Update the HTML with actual scene durations and subtitle timing data"""
        # Convert data to JSON strings
        durations_json = json.dumps(scene_durations, ensure_ascii=True)
        subtitle_json = json.dumps(subtitle_data, ensure_ascii=True)
        
        # Replace durations placeholder
        start_marker = "/*DURATIONS*/"
        end_marker = "/*END*/"
        
        start_idx = html_content.find(start_marker)
        if start_idx != -1:
            end_idx = html_content.find(end_marker, start_idx)
            if end_idx != -1:
                html_content = (
                    html_content[:start_idx] + 
                    durations_json + 
                    html_content[end_idx + len(end_marker):]
                )
        
        # Replace subtitle data
        subtitle_pattern = "let subtitleData = [];"
        subtitle_replacement = f"let subtitleData = {subtitle_json};"
        html_content = html_content.replace(subtitle_pattern, subtitle_replacement)
        
        return html_content


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    from .script_generator import ScriptGenerator
    
    test_post = """
    🚀 Just shipped a feature that reduced our API response time by 73%!
    
    The result? Our users are happier and our costs dropped by 40%.
    """
    
    script_gen = ScriptGenerator()
    code_gen = CodeGenerator()
    
    script = script_gen.generate_script(test_post, "16:9")
    html_code = code_gen.generate_code(script, "16:9")
    
    with open("test_output.html", "w") as f:
        f.write(html_code)
    
    print("Generated HTML saved to test_output.html")
