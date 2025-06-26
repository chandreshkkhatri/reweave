"""
Build Video from Content and template
"""

import moviepy.editor as mp
from reweave.utils.env_utils import is_interactive

from .graphical_story_repo import GraphicalStoryRepo
from .story_builder import ScriptBuilder


class GraphicalStoryWorkflow:
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
            # Delegate generation to repository
            self.graphical_story_repo.save_scene_image(
                content_id,
                idx,
                script.title,
                script.story_summary,
                script.visual_style_description,
                script.characters,
                scene
            )
            self.graphical_story_repo.save_scene_audio(
                content_id,
                idx,
                scene.get("narration")
            )
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

    def generate_video(self, content_id, title, additional_instructions=None):
        """
        Generate video
        """
        self.create_story(content_id, title, additional_instructions)
        self.generate_script(content_id)
        self.generate_footages(content_id)
        self.generate_final_video(content_id)
