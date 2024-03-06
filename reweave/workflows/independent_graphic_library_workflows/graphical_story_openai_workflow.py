"""
Build Video from Content and template
"""

import json
import requests
import moviepy.editor as mp
from pathlib import Path

from reweave.utils.fs_utils import read_content_from_file, write_content_to_file
from .base_workflow import BaseWorkflow
from ...ai.openai_service import generate_audio, generate_image, client


OUTPUT_DIR = Path('data/output/graphical_story')

class GraphicalStoryWorkflow(BaseWorkflow):
    
    def __init__(self, topic=None):
        self.topic = topic
        self.story = None
        self.script = None
        self.footages = []
        self.audio = []
        self.output_dir = f'{OUTPUT_DIR}/{self.topic[:20]}'
        

    def generate_story(self):
        prompt = f"""
                You are a helpful assistant writer. Write the story for the following topic: {self.topic}
                
                Provide a good narrative structure for the story describing the plot, characters, and setting.
                
                Follow the following guidelines to create a good narrative:
                1. Opener:
                The opener establishes your story’s setting, premise, plot, and character roles. A compelling opener teases readers with what challenges or conflicts are ahead.

                2. Incident
                Stage two is the story’s incident. As the catalyst or instigating force that compels your main character to act, the incident establishes the conflict that sets the stage for the third phase of a story’s structure. 

                3. Crisis
                As a consequence of the incident, the story’s crisis is an unfolding of the primary conflict or series of issues. A crisis must be realistic and related to the plot. If the character experiences more than one crisis, each should build on the last, heightening the sense of danger and tension.

                4. Climax
                Stage four is the climax or the height of the crisis. Depending on your perspective, you can also think of the climax as the bottom of your action. At this stage, the character has hit rock bottom in the storyline–hopeless and seemingly out of options. The climax is not the end of the book but the beginning of the end.

                5. Ending
                The final stage of the story structure is the ending or close. Success or failure are both valid outcomes, but the ending should provide a conclusion and resolution to your story. The ending should close the loop on all crises, plot twists, and loose ends but could also leave the reader wanting more. 
            """
        try:
            response = client.chat.completions.create(
                    model="gpt-4-1106-preview",  # You can change the model version if needed
                    messages=[{
                        "role": "system",  
                        "content": prompt
                    }],
                )
            story = response.choices[0].message.content

            if story:
                self.story = story
                self._write_to_file(story, 'story.txt')
                return json.loads(story)

        except Exception as e:
            print(f"An error occurred: {e}")

        
        
    
    def generate_script(self):
        self.story = read_content_from_file('story.txt', self.output_dir)
        
        prompt = f"""
                You are a helpful assistant. Use the story provided below to write a script.
                
                Provide detailed character descriptions for each character including their name, age, gender, description, their personality, and any other relevant information.
                Also provide a very detailed description of their looks which can be used to independently create similar images from various artists for different panels.
                For each scene, provide a background description, a narration, a list of characters in the scene, and a list of dialogues.
                Also describe the bodylanguage of characters in the description.
                
                The story is as follows: {self.story}
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
                self._write_to_file(script, 'script.json')
                return json.loads(script)

        except Exception as e:
            print(f"An error occurred: {e}")


    def _write_to_file(self, content, filename):
        """
        Write the script to a file
        """
        write_content_to_file(content, filename, self.output_dir)

    def generate_footages(self):
        script = json.loads(read_content_from_file('script.json', self.output_dir))
        scene_list = script.get("scene_list")
        title = script.get("title")
        summary = script.get("story_summary")
        visual_style_description = script.get("visual_style_description")
        characters = script.get("characters")
            
        for idx, scene in enumerate(scene_list):
            self._generate_scene_image(self.topic, idx, title, summary, visual_style_description, characters, scene)
            self._generate_scene_audio(idx, scene, self.topic)
        
    def _generate_scene_image(self, topic, panel_number, title, summary, visual_style_description, characters, scene):
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
        Path(f"{self.output_dir}/{panel_number+1}.png").write_bytes(image)

    def _generate_scene_audio(self, panel_number, scene, topic):
        """
        Create an audio
        """
        scene_narration = scene.get("narration")
        if scene_narration is None:
            return

        audio = generate_audio(scene_narration)
        audio.stream_to_file(f"{self.output_dir}/{panel_number+1}.mp3")
            

    def generate_final_video(self):
        """
        Create a video
        """
        video_clips = []
        start = 0
        script = json.loads(read_content_from_file('script.json', self.output_dir))
        scene_list = script.get("scene_list")
        
        for idx, clip_content in enumerate(scene_list):
            image_clip = mp.ImageClip(
                f"{self.output_dir}/{idx+1}.png",
            )
            audio_clip = mp.AudioFileClip(
                f"{self.output_dir}/{idx+1}.mp3"
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
        
        video.write_videofile(f"{self.output_dir}/final_video.mp4", fps=24, remove_temp=False)
        
        
    def generate_video(self):
        self.generate_script()
        self.generate_footages()
        self.generate_final_video()
