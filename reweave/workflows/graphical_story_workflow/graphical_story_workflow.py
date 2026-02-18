"""
Build Video from Content and template
"""

from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, vfx
from reweave.utils.env_utils import is_interactive
from reweave.utils.video_utils import create_title_card

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
        Create story. Skipped if an identical story is already cached.
        """
        if self.graphical_story_repo.is_story_cached(content_id, title, additional_instructions):
            if is_interactive():
                print(f"[cache] story for '{content_id}' is up-to-date, skipping generation.")
            return
        story = self.script_builder.generate_story(
            title, additional_instructions)
        self.graphical_story_repo.create_story(content_id, story, title, additional_instructions)

    def generate_script(self, content_id):
        """
        Generate script. Skipped if an identical script is already cached.
        """
        if self.graphical_story_repo.is_script_cached(content_id):
            if is_interactive():
                print(f"[cache] script for '{content_id}' is up-to-date, skipping generation.")
            return
        story = self.graphical_story_repo.get_story(content_id)
        script = self.script_builder.generate_script(story)
        self.graphical_story_repo.create_script(content_id, script)

    def generate_footages(self, content_id):
        """
        Generate footages. Individual scenes are skipped if already cached.
        """
        script = self.graphical_story_repo.get_script(content_id)
        scene_list = script.scene_list

        for idx, scene in enumerate(scene_list):
            if self.graphical_story_repo.is_scene_cached(
                content_id, idx,
                script.title, script.visual_style_description,
                script.characters, scene,
            ):
                if is_interactive():
                    print(f"[cache] scene {idx+1}/{len(scene_list)} is up-to-date, skipping.")
                continue

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
                scene.narration,
                scene,
            )
            if is_interactive():
                print(f"Generated {idx+1} of {len(scene_list)}")

    def generate_final_video(self, content_id):
        """
        Create a video with title card and crossfade transitions between scenes.
        """
        crossfade = 1.0  # seconds
        video_clips = []
        audio_clips = []
        script = self.graphical_story_repo.get_script(content_id)
        footage_uri = self.graphical_story_repo.get_footage_uri(content_id)
        scene_list = script.scene_list

        try:
            # Title card (3 seconds)
            title_clip = create_title_card(
                script.title, duration=3,
                width=1024, height=1024,
            ).with_start(0)
            video_clips.append(title_clip)
            start = 3 - crossfade  # overlap with first scene

            for idx in range(len(scene_list)):
                image_clip = ImageClip(f"{footage_uri}/{idx+1}.png")
                audio_clip = AudioFileClip(f"{footage_uri}/{idx+1}.mp3")
                audio_clips.append(audio_clip)
                duration = audio_clip.duration

                image_clip = image_clip.with_start(start).with_duration(duration)
                image_clip = image_clip.with_effects([vfx.CrossFadeIn(crossfade)])
                audio_clip = audio_clip.with_start(start)

                clip = image_clip.with_audio(audio_clip)
                video_clips.append(clip)
                start += duration - crossfade

            video = CompositeVideoClip(video_clips)
            self.graphical_story_repo.create_video(content_id, video)
        finally:
            for clip in audio_clips:
                clip.close()

    def generate_video(self, content_id, title, additional_instructions=None):
        """
        Generate video
        """
        self.create_story(content_id, title, additional_instructions)
        self.generate_script(content_id)
        self.generate_footages(content_id)
        self.generate_final_video(content_id)
