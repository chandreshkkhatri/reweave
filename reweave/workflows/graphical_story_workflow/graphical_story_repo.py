"""
Repo for Graphical Story
"""
import hashlib
import json
import os
from pathlib import Path

from reweave.utils.fs_utils import read_content_from_file, write_content_to_file, write_bytes_to_file, write_stream_to_file
from .commons import Script
from .story_builder import STORY_PROMPT_HASH, SCRIPT_PROMPT_HASH
from ...ai.gemini_service import (
    generate_image, generate_audio,
    DEFAULT_TEXT_MODEL, DEFAULT_IMAGE_MODEL, FALLBACK_IMAGE_MODEL, DEFAULT_TTS_MODEL,
)

OUTPUT_DIR = Path(os.getenv('REWEAVE_OUTPUT_DIR', 'data/output')) / 'graphical_story'
STORY_FILENAME = 'story.txt'
SCRIPT_FILENAME = 'script.json'
VIDEO_FILENAME = 'final_video.mp4'
CACHE_FILENAME = 'cache.json'


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _make_hash(*parts) -> str:
    """Return a short SHA-256 hex digest of the concatenated string parts."""
    combined = "\n".join(str(p) for p in parts)
    return hashlib.sha256(combined.encode()).hexdigest()


def _load_cache(output_dir: str) -> dict:
    cache_path = Path(output_dir) / CACHE_FILENAME
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(output_dir: str, cache: dict) -> None:
    cache_path = Path(output_dir) / CACHE_FILENAME
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2))


# Scene image prompt template — static wrapper text whose hash is included in cache keys
_SCENE_IMAGE_PROMPT_TEMPLATE = """
    Create a single illustration for a story.
    Composition guidelines:
    - Frame the scene with clear foreground subjects and a contextual background.
    - Use lighting and color palette that match the mood of the narration.
    - Show character emotions through facial expressions and body language.
    - Maintain visual consistency with the described art style throughout.
    - Fill the entire frame with no borders or letterboxing.
    - IMPORTANT: The image must contain absolutely NO text, letters, numbers, words,
      titles, captions, labels, subtitles, speech bubbles, thought bubbles, signs with
      readable text, or watermarks of any kind. Pure illustration only.
"""
_SCENE_IMAGE_PROMPT_HASH = _make_hash(_SCENE_IMAGE_PROMPT_TEMPLATE)


class GraphicalStoryRepo:
    """
    Repo for Graphical Story
    """

    def is_story_cached(self, content_id, title, additional_instructions) -> bool:
        """Return True if a story with these exact inputs already exists."""
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        cache = _load_cache(output_dir)
        expected = _make_hash(title, additional_instructions or "", DEFAULT_TEXT_MODEL, STORY_PROMPT_HASH)
        return cache.get("story_hash") == expected

    def create_story(self, content_id, story, title, additional_instructions):
        """
        Create story and record its input hash in the cache.
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        write_content_to_file(story, STORY_FILENAME, output_dir)
        cache = _load_cache(output_dir)
        cache["story_hash"] = _make_hash(title, additional_instructions or "", DEFAULT_TEXT_MODEL, STORY_PROMPT_HASH)
        _save_cache(output_dir, cache)

    def get_story(self, content_id):
        """
        Get story
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        return read_content_from_file(STORY_FILENAME, output_dir)

    def is_script_cached(self, content_id) -> bool:
        """Return True if a script generated from the current story & model already exists."""
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        cache = _load_cache(output_dir)
        story_hash = cache.get("story_hash", "")
        expected = _make_hash(story_hash, DEFAULT_TEXT_MODEL, SCRIPT_PROMPT_HASH)
        return cache.get("script_hash") == expected

    def create_script(self, content_id, script):
        """
        Create Script and record its input hash in the cache.
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        write_content_to_file(script, SCRIPT_FILENAME, output_dir)
        cache = _load_cache(output_dir)
        story_hash = cache.get("story_hash", "")
        cache["script_hash"] = _make_hash(story_hash, DEFAULT_TEXT_MODEL, SCRIPT_PROMPT_HASH)
        cache.setdefault("scenes", {})
        _save_cache(output_dir, cache)

    def get_script(self, content_id):
        """
        Get script
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'

        script = json.loads(read_content_from_file(
            SCRIPT_FILENAME, f'{output_dir}'))
        script_model_instance = Script.model_validate(script)
        return script_model_instance

    def create_video(self, content_id, video):
        """
        Create video
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        video.write_videofile(
            f"{output_dir}/{VIDEO_FILENAME}", fps=24,
            codec='libx264', audio_codec='aac',
            temp_audiofile=f'temp-story-audio-{os.getpid()}.m4a',
            remove_temp=True)
        video.close()

    def get_footage_uri(self, content_id):
        """
        Get footage uri
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        return output_dir

    def _scene_image_hash(self, title, visual_style_description, characters, scene) -> str:
        return _make_hash(
            title, visual_style_description,
            json.dumps(characters, sort_keys=True),
            scene.scene_description, scene.narration,
            json.dumps(scene.characters_in_scene),
            DEFAULT_IMAGE_MODEL, FALLBACK_IMAGE_MODEL,
            _SCENE_IMAGE_PROMPT_HASH,
        )

    def _scene_audio_hash(self, scene) -> str:
        return _make_hash(scene.narration, DEFAULT_TTS_MODEL)

    def is_scene_cached(self, content_id, panel_number, title, visual_style_description, characters, scene) -> bool:
        """Return True if both image and audio for this scene already exist with matching hashes."""
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        cache = _load_cache(output_dir)
        scene_cache = cache.get("scenes", {}).get(str(panel_number), {})
        image_ok = scene_cache.get("image_hash") == self._scene_image_hash(
            title, visual_style_description, characters, scene)
        audio_ok = scene_cache.get("audio_hash") == self._scene_audio_hash(scene)
        return image_ok and audio_ok

    def save_scene_image(self, content_id, panel_number, title, summary, visual_style_description, characters, scene):
        """
        Generate and save a scene image using AI and write to file
        """
        scene_description = scene.scene_description
        narration = scene.narration
        characters_in_scene = scene.characters_in_scene
        prompt = f"""
            Create a single illustration for a story titled "{title}".

            Visual style: {visual_style_description}

            Characters in this scene: {json.dumps(characters_in_scene)}
            Character reference descriptions: {json.dumps(characters)}

            Scene description: {scene_description}
            Scene narration: {narration}

            Composition guidelines:
            - Frame the scene with clear foreground subjects and a contextual background.
            - Use lighting and color palette that match the mood of the narration.
            - Show character emotions through facial expressions and body language.
            - Maintain visual consistency with the described art style throughout.
            - Fill the entire frame with no borders or letterboxing.
            - IMPORTANT: The image must contain absolutely NO text, letters, numbers, words,
              titles, captions, labels, subtitles, speech bubbles, thought bubbles, signs with
              readable text, or watermarks of any kind. Pure illustration only.
        """
        image_bytes = generate_image(prompt)
        if not image_bytes:
            raise RuntimeError(
                f"Failed to generate image for scene {panel_number}")
        write_bytes_to_file(
            image_bytes, f"{panel_number+1}.png", f"{OUTPUT_DIR}/{content_id}")
        # Update image hash in cache
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        cache = _load_cache(output_dir)
        cache.setdefault("scenes", {}).setdefault(str(panel_number), {})["image_hash"] = (
            self._scene_image_hash(title, visual_style_description, characters, scene)
        )
        _save_cache(output_dir, cache)

    def save_scene_audio(self, content_id, panel_number, narration, scene=None):
        """
        Generate and save scene audio using AI and write to file
        """
        if not narration:
            return
        audio_stream = generate_audio(narration)
        write_stream_to_file(
            audio_stream, f"{panel_number+1}.mp3", f"{OUTPUT_DIR}/{content_id}")
        if scene is not None:
            output_dir = f'{OUTPUT_DIR}/{content_id}'
            cache = _load_cache(output_dir)
            cache.setdefault("scenes", {}).setdefault(str(panel_number), {})["audio_hash"] = (
                self._scene_audio_hash(scene)
            )
            _save_cache(output_dir, cache)
