"""
Create a monologue video template
"""
from chitralok.utils.fs_utils import write_script_to_file
from chitralok.video_builder_workflow.base_workflow import BaseWorkflow
from ..ai.openai_service import client


class MonologueWorkflow(BaseWorkflow):
    """
    Create a monologue video template
    """

    def __init__(self, script=None, topic=None, narrator_name=None):
        self.script = script
        self.topic = topic
        self.narrator_name = narrator_name
        
    def generate_script(self):
        """
        Create a monologue script 
        """
        if self.narrator_name:
            narrator_prompt_placeholder = f'named {self.narrator_name}'
        else:
            narrator_prompt_placeholder = ', choose a suitable name for yourself'
            
        prompt = f"""
            You are to play the role of a narrator {narrator_prompt_placeholder}. You have to write a short script for the topic: {self.topic} in form of a monologue.
            The monologue will be given a the narrator in form of a presentation on a TV show.             
            Provide the title, narrator's physical features and the description of the monologue.
            Provide the backdrop of the monologue and the monologue itself.
            Keep the length of the monologue to 10 to 15 sentences.
            Try to keep the monologue feel complete in itself taking it through a story arc with a setup, arguements, and conclusion.
        """
        
        functions = [
            {
                "name": "create_monologue_script",
                "description": "Create a monologue script",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "narrator_name": {
                            "type": "string"                            
                        },
                        "narrator_description": {
                            "type": "string"
                        },
                        "monologue_context": {
                            "type": "string"
                        },
                        "dialogue": {
                            "type": "string"
                        },
                    },
                    "required": ["title", "narrator_name", "narrator_description", "monologue_context", "dialogue"]
                }
            }
        ]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": prompt},
                ],
                functions=functions,
                function_call={"name": "create_monologue_script"},
            )
            
            resp_args = response.choices[0].message.function_call.arguments
            
            if resp_args:
                self.write_script_to_file(resp_args)
            else:
                return None
            
        except Exception as e:
            print(e)
            return None

    def write_script_to_file(self, script):
        """
        Write the script to a file
        """
        write_script_to_file(script, 'script.json', f'data/output/monologue/{self.topic[:20]}')

