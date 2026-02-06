"""
Repo for Graphical Story
"""
import json
import os
from pathlib import Path

from reweave.utils.fs_utils import read_content_from_file, write_content_to_file, write_bytes_to_file, write_stream_to_file
from .commons import Script
from ...ai.gemini_service import generate_image, generate_audio

OUTPUT_DIR = Path(os.getenv('REWEAVE_OUTPUT_DIR', 'data/output')) / 'graphical_story'
STORY_FILENAME = 'story.txt'
SCRIPT_FILENAME = 'script.json'
VIDEO_FILENAME = 'final_video.mp4'


class GraphicalStoryRepo:
    """
    Repo for Graphical Story
    """

    def create_story(self, content_id, story):
        """
        Create story
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        write_content_to_file(story, STORY_FILENAME, output_dir)

    def get_story(self, content_id):
        """
        Get story
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        return read_content_from_file(STORY_FILENAME, output_dir)

    def create_script(self, content_id, script):
        """
        Create Script
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        write_content_to_file(script, SCRIPT_FILENAME, output_dir)

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

    def save_scene_image(self, content_id, panel_number, title, summary, visual_style_description, characters, scene):
        """
        Generate and save a scene image using AI and write to file
        """
        scene_description = scene.scene_description
        narration = scene.narration
        characters_in_scene = scene.characters_in_scene
        prompt = f"""
            The image to be created is a panel of a story titled \"{title}\" with the following characters: {json.dumps(characters)}.
            The summary of the story is \"{summary}\".
            The visual style of the story as follows \"{visual_style_description}\".
            The story is divided into scenes and you have to draw one of the scenes.
            The scene contains the following characters: {json.dumps(characters_in_scene)}.
            The scene description is \"{scene_description}\"    
            The following is a background narration in the scene: \"{narration}\"
            Do not add any text to the images.
        """
        image_bytes = generate_image(prompt)
        if not image_bytes:
            raise RuntimeError(
                f"Failed to generate image for scene {panel_number}")
        write_bytes_to_file(
            image_bytes, f"{panel_number+1}.png", f"{OUTPUT_DIR}/{content_id}")

    def save_scene_audio(self, content_id, panel_number, narration):
        """
        Generate and save scene audio using AI and write to file
        """
        if not narration:
            return
        audio_stream = generate_audio(narration)
        write_stream_to_file(
            audio_stream, f"{panel_number+1}.mp3", f"{OUTPUT_DIR}/{content_id}")
