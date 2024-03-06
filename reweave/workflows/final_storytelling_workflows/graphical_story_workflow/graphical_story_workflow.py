"""
Build Video from Content and template
"""

import json
import requests
import moviepy.editor as mp
from reweave.utils.env_utils import is_interactive

from reweave.utils.fs_utils import write_bytes_to_file, write_stream_to_file
from .graphical_story_repo import GraphicalStoryRepo
from .story_builder import ScriptBuilder
from ..base_workflow import BaseWorkflow
from ....ai.openai_service import generate_audio, generate_image


class GraphicalStoryWorkflow(BaseWorkflow):
    """
    Build Video from Content and template
    """

    def __init__(self):
        self.graphical_story_repo = GraphicalStoryRepo()
        self.script_builder = ScriptBuilder()

    def create_story(self, content_id, title, additional_instructions=None):
        """
        Create story
        """
        story = self.script_builder.generate_story(
            title, additional_instructions)
        self.graphical_story_repo.create_story(content_id, story)

    def generate_script(self, content_id):
        """
        Generate script
        """
        story = self.graphical_story_repo.get_story(content_id)
        script = self.script_builder.generate_script(story)
        self.graphical_story_repo.create_script(content_id, script)

    def generate_footages(self, content_id):
        """
        Generate footages
        """
        footage_uri = self.graphical_story_repo.get_footage_uri(content_id)
        script = self.graphical_story_repo.get_script(content_id)
        scene_list = script.scene_list

        for idx, scene in enumerate(scene_list):
            self._generate_scene_image(
                idx,
                script.title,
                script.story_summary,
                script.visual_style_description,
                script.characters,
                scene,
                footage_uri)
            self._generate_scene_audio(idx, scene, footage_uri)
            if is_interactive():
                print(f"Generated {idx+1} of {len(scene_list)}")

    def generate_final_video(self, content_id):
        """
        Create a video
        """
        video_clips = []
        start = 0
        script = self.graphical_story_repo.get_script(content_id)
        footage_uri = self.graphical_story_repo.get_footage_uri(content_id)
        scene_list = script.scene_list

        for idx in range(len(scene_list)):
            image_clip = mp.ImageClip(
                f"{footage_uri}/{idx+1}.png",
            )
            audio_clip = mp.AudioFileClip(
                f"{footage_uri}/{idx+1}.mp3"
            )
            duration = audio_clip.duration
            image_clip = image_clip.set_start(start)
            image_clip = image_clip.set_duration(duration)
            audio_clip = audio_clip.set_start(start)
            clip = image_clip.set_audio(audio_clip)
            clip = clip.set_duration(duration)
            start += duration
            video_clips.append(clip)

        video = mp.CompositeVideoClip(video_clips)

        self.graphical_story_repo.create_video(content_id, video)

    def _generate_scene_image(self, panel_number, title, summary, visual_style_description, characters, scene, footage_dest):
        """
        Create an image
        """
        scene_description = scene.get("scene_description")
        narration = scene.get("narration")
        characters_in_scene = scene.get("characters_in_scene")
        prompt = f"""
            The image to be created is a panel of a story titled "{title}" with the following characters: {json.dumps(characters)}.
            The summary of the story is "{summary}".
            The visual style of the story as follows "{visual_style_description}".
            The story is divided into scenes and you have to draw one of the scenes.
            The scene contains the following characters: {json.dumps(characters_in_scene)}.
            The scene description is "{scene_description}"    
            The following is a background narration in the scene: "{narration}"
            Do not add any text to the images.
        """
        image_url = generate_image(prompt)
        image = requests.get(image_url).content
        write_bytes_to_file(image, f"{panel_number+1}.png", footage_dest)

    def _generate_scene_audio(self, panel_number, scene, footage_dest):
        """
        Create scene audio
        """
        scene_narration = scene.get("narration")
        if scene_narration is None:
            return

        audio = generate_audio(scene_narration)
        write_stream_to_file(audio, f"{panel_number+1}.mp3", footage_dest)

    def generate_video(self, content_id, title, additional_instructions=None):
        """
        Generate video
        """
        self.create_story(content_id, title, additional_instructions)
        self.generate_script(content_id)
        self.generate_footages(content_id)
        self.generate_final_video(content_id)
