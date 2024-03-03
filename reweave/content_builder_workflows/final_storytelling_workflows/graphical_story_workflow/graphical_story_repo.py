"""
Repo for Graphical Story
"""
import json
from pathlib import Path

from reweave.utils.fs_utils import read_content_from_file, write_content_to_file
from .commons import Script, Scene

OUTPUT_DIR = Path('data/output/graphical_story')
STORY_FILENAME = 'story.txt'
SCRIPT_FILENAME = 'script.json'
VIDEO_FILENAME = 'final_video.mp4'

class GraphicalStoryRepo:
    """
    Repo for Graphical Story
    """

    def __init__(self):
        pass

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
        
        script = json.loads(read_content_from_file(SCRIPT_FILENAME, f'{output_dir}'))
        script_model_instance = Script.model_validate(script)
        return script_model_instance

    def create_video(self, content_id, video):
        """
        Create video
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        video.write_videofile(f"{output_dir}/{VIDEO_FILENAME}", fps=24, remove_temp=False)


    def get_footage_uri(self, content_id):
        """
        Get footage uri
        """
        output_dir = f'{OUTPUT_DIR}/{content_id}'
        return output_dir