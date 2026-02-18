"""
Story Builder class
"""

import hashlib

from .commons import NarrativeStructurePrompts
from ...ai.gemini_service import generate_text


# ---------------------------------------------------------------------------
# Prompt templates (module-level so changes automatically bust the cache)
# ---------------------------------------------------------------------------

_STORY_PROMPT_TEMPLATE = """
    You are an experienced fiction writer known for vivid, emotionally engaging stories.
    Write a complete short story for the following topic: {{title}}

    {{additional_instructions}}

    Follow these guidelines for a compelling narrative:

    {narrative_structure}

    Additional writing requirements:
    - Create distinct, memorable characters with clear motivations.
    - Use sensory details: describe what characters see, hear, smell, and feel.
    - Include meaningful dialogue that reveals character personality.
    - Build tension through escalating stakes and obstacles.
    - End with a satisfying resolution that feels earned.
    - Use vivid visual descriptions for settings and actions — these will be used to generate illustrations.
    - Aim for 800-1200 words, enough depth for 6-8 illustrated scenes.

    Write the story as flowing prose. Do not label acts or sections.
""".format(narrative_structure=NarrativeStructurePrompts.three_act_narrative)

_SCRIPT_PROMPT_TEMPLATE = """
    You are a helpful screenwriter. Use the story provided below to write a script.

    Provide detailed character descriptions for each character including their name, age, gender,
    description, their personality, and any other relevant information.
    Also provide a very detailed description of their looks which can be used to independently
    create similar images from various artists for different panels.
    For each scene, provide a background description, the list of characters and a narration.

    The story is as follows: {{story}}
"""


def _template_hash(template: str) -> str:
    return hashlib.sha256(template.encode()).hexdigest()


STORY_PROMPT_HASH = _template_hash(_STORY_PROMPT_TEMPLATE)
SCRIPT_PROMPT_HASH = _template_hash(_SCRIPT_PROMPT_TEMPLATE)


class ScriptBuilder:
    """
    Class to build script and related parts for of the workflow
    """
    def __init__(self):
        pass


    def generate_story(self, title, additional_instructions=None):
        """
        Generate story
        """
        prompt = f"""
                You are an experienced fiction writer known for vivid, emotionally engaging stories.
                Write a complete short story for the following topic: {title}

                {additional_instructions or ""}

                Follow these guidelines for a compelling narrative:

                {NarrativeStructurePrompts.three_act_narrative}

                Additional writing requirements:
                - Create distinct, memorable characters with clear motivations.
                - Use sensory details: describe what characters see, hear, smell, and feel.
                - Include meaningful dialogue that reveals character personality.
                - Build tension through escalating stakes and obstacles.
                - End with a satisfying resolution that feels earned.
                - Use vivid visual descriptions for settings and actions — these will be used to generate illustrations.
                - Aim for 800-1200 words, enough depth for 6-8 illustrated scenes.

                Write the story as flowing prose. Do not label acts or sections.
            """
        response = generate_text(system_prompt=prompt)
        if not response.content:
            raise RuntimeError("Story generation returned empty content")
        return response.content


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
                                },
                                "required": ["scene_number", "scene_description", "narration", "characters_in_scene"]
                            }
                        },
                    },
                    "required": ["title", "story_summary", "visual_style_description", "characters", "scene_list"]
                }
            }
        ]

        response = generate_text(
            system_prompt=prompt,
            functions=functions,
            function_call={"name": "create_script"},
        )
        if not response.function_call:
            raise RuntimeError("Script generation did not return a function call")
        return response.function_call.arguments

