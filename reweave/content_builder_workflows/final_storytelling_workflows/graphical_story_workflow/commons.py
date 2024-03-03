from enum import Enum
from pydantic import BaseModel

class NarrativeStructurePrompts(Enum):
    """
    Narrative Structure Prompts
    """
    three_act_narrative = """
        The First Act (Setup): This act sets the stage by introducing the main character, their relationships, the world they live in, and the initial conflict. 
        The Second Act (Confrontation): As the heart of the story, this act is a turning point that involves the main character encountering increasing challenges and obstacles as they work to resolve climactic challenges. 
        The Third Act (Resolution): This final act brings the story to a close, resolving the conflict and tying up loose ends. The third act reveals the consequences and outcomes of the character’s actions.
        """


    def __str__(self):
        return str(self.value)
    

    def __repr__(self):
        return str(self.value)
    
    
class Scene(BaseModel):
    """
    Scene
    """
    scene_description: str
    characters_in_scene: list
    narration: str
    
    
class Script(BaseModel):
    """
    Script
    """
    title: str
    story_summary: str
    visual_style_description: str
    characters: list
    scene_list: list