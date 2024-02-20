"""
Build Video from Content and template
"""

import json
import requests
import moviepy.editor as mp
from pathlib import Path

from reweave.utils.fs_utils import write_script_to_file
from reweave.video_builder_workflow.base_workflow import BaseWorkflow
from ..ai.openai_service import generate_audio, generate_image, client
    

OUTPUT_DIR = Path('data/output/graphical_story')

class GraphicalStoryWorkflow(BaseWorkflow):
    
    def __init__(self, script=None, topic=None):
        self.script = script
        self.topic = topic
        self.footages = []
        self.audio = []
        
        
    def generate_script(self, topic):
        """
        Create a video script
        """
        
        prompt = f"""
                You are a helpful assistant. Create a short script for the topic: {topic}
                
                Provide detailed character descriptions for each character including their name, age, gender, description, their personality, and any other relevant information.
                Also provide a very detailed description of their looks which can be used to independently create similar images from various artists for different panels.
                For each scene, provide a background description, a narration, a list of characters in the scene, and a list of dialogues.
                Also describe the bodylanguage of characters in the description.
            """
        functions = [
            {
                "name": "write_script_to_file",
                "description": "Writes the script to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "story_summary": {
                            "type": "string"
                        },
                        "visual_style_description": {
                            "type": "string"
                        },
                        "characters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    }
                                }
                            }
                        },
                        "scene_list": {
                            "type": "array",         
                            "items": {
                                "type": "object",
                                "properties": {
                                    "scene_number": {
                                        "type": "integer"
                                    },
                                    "scene_description": {
                                        "type": "string"
                                    },
                                    "narration": {
                                        "type": "string"
                                    },
                                    "characters_in_scene": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                }
                            },
                            "required": ["scene_number", "scene_description", "narration", "characters_in_scene"]
                        },
                    },
                    "required": ["title", "story_summary", "visual_style_description", "characters", "scene_list"]
                }
            }
        ]

        try:
            response = client.chat.completions.create(
                    model="gpt-4-1106-preview",  # You can change the model version if needed
                    messages=[{
                        "role": "system",  
                        "content": prompt
                    }],
                    functions=functions,
                    function_call={"name": "write_script_to_file"}
                )
            script = response.choices[0].message.function_call.arguments
            if script:
                self.script = script
                self.write_script_to_file(script)
                return json.loads(script)

        except Exception as e:
            print(f"An error occurred: {e}")


    def write_script_to_file(self, script):
        """
        Write the script to a file
        """
        write_script_to_file(script, 'script.json', f'{OUTPUT_DIR}/{self.topic[:20]}')

    def generate_footages(self, script, topic):
        scene_list = script.get("scene_list")
        title = script.get("title")
        summary = script.get("story_summary")
        visual_style_description = script.get("visual_style_description")
        characters = script.get("characters")
            
        for idx, scene in enumerate(scene_list):
            self.generate_scene_image(topic, idx, title, summary, visual_style_description, characters, scene)
            self.generate_scene_audio(idx, scene, topic)
        
    def generate_scene_image(self, topic, panel_number, title, summary, visual_style_description, characters, scene):
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
        Path(f"{OUTPUT_DIR}/{topic}/{panel_number+1}.png").write_bytes(image)

    def generate_scene_audio(self, panel_number, scene, topic):
        """
        Create an audio
        """
        scene_narration = scene.get("narration")
        if scene_narration is None:
            return

        audio = generate_audio(scene_narration)
        audio.stream_to_file(f"{OUTPUT_DIR}/{topic}/{panel_number+1}.mp3")
            

    def generate_video(self, script):
        """
        Create a video
        """
        video_clips = []
        start = 0
        scene_list = script.get("scene_list")
        
        for idx, clip_content in enumerate(scene_list):
            image_clip = mp.ImageClip(
                f"data/output/{self.topic}/{idx+1}-{clip_content['name']}.png",
            )
            audio_clip = mp.AudioFileClip(
                f"data/output/{self.topic}/{idx+1}-{clip_content['name']}.mp3"
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
        
        video.write_videofile(f"data/output/{self.topic}/final_video.mp4", fps=24, remove_temp=False)
