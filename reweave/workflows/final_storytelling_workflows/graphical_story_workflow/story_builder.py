"""
Story Builder class
"""

from .commons import NarrativeStructurePrompts
from ....ai.openai_service import client

class ScriptBuilder:
    """
    Class to build script and related parts for of the workflow
    """
    def __init__(self):
        pass
    
    
    def generate_story(self, title, additional_instructions = None):
        """
        Generate story
        """
        prompt = f"""
                You are a helpful assistant writer. Write the story for the following topic: {title}
                
                {additional_instructions}
                
                Provide a good narrative structure for the story describing the plot, characters, and setting.
                
                Follow the following guidelines to create a good narrative:
                
                {NarrativeStructurePrompts.three_act_narrative}
                
                Try to follow the guidelines implicitely, but do not explicitely breakdown the story into different parts. Simply reply with the story.
            """
        try:
            response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    messages=[{
                        "role": "system",  
                        "content": prompt
                    }],
                )
            story = response.choices[0].message.content

            if story:
                return story

        except Exception as e:
            print(f"An error occurred while generating the story: {e}")
            
            
    def generate_script(self, story):
        prompt = f"""
        You are a helpful screenwriter. Use the story provided below to write a script.
        
        Provide detailed character descriptions for each character including their name, age, gender, description, their personality, and any other relevant information.
        Also provide a very detailed description of their looks which can be used to independently create similar images from various artists for different panels.
        For each scene, provide a background description, the list of characters and a narration for the scene.
        
        The story is as follows: {story}
            """
        functions = [
            {
                "name": "create_script",
                "description": "Creates a script for the story with necessary fulfilling requirements",
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
                    function_call={"name": "create_script"}
                )
            script_response = response.choices[0].message.function_call.arguments
            if script_response:
                return script_response

        except Exception as e:
            print(f"An error occurred while generating the script: {e}")

