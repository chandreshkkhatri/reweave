import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Mock external dependencies before importing
sys.modules['google'] = MagicMock()
sys.modules['google.genai'] = MagicMock()
sys.modules['google.genai.types'] = MagicMock()
sys.modules['gtts'] = MagicMock()
sys.modules['moviepy'] = MagicMock()

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)


def test_graphical_story_workflow_imports():
    """Test that we can import the workflow class."""
    from reweave.workflows.graphical_story_workflow.graphical_story_workflow import GraphicalStoryWorkflow
    assert GraphicalStoryWorkflow is not None


def test_graphical_story_workflow_init():
    """Test workflow initialization creates builder and repo."""
    from reweave.workflows.graphical_story_workflow.graphical_story_workflow import GraphicalStoryWorkflow

    workflow = GraphicalStoryWorkflow()
    assert workflow.graphical_story_repo is not None
    assert workflow.script_builder is not None


def test_graphical_story_commons_scene_model():
    """Test the Scene Pydantic model with typed fields."""
    from reweave.workflows.graphical_story_workflow.commons import Scene

    scene = Scene(
        scene_number=1,
        scene_description="A forest clearing",
        characters_in_scene=["Alice", "Bob"],
        narration="They walked into the clearing.",
    )
    assert scene.scene_number == 1
    assert scene.scene_description == "A forest clearing"
    assert scene.characters_in_scene == ["Alice", "Bob"]
    assert scene.narration == "They walked into the clearing."


def test_graphical_story_commons_script_model():
    """Test the Script Pydantic model with typed scene_list."""
    from reweave.workflows.graphical_story_workflow.commons import Script, Scene

    scene = Scene(
        scene_number=1,
        scene_description="A forest",
        characters_in_scene=["Alice"],
        narration="Once upon a time.",
    )
    script = Script(
        title="Test Story",
        story_summary="A test summary",
        visual_style_description="Watercolor",
        characters=[{"name": "Alice", "description": "A curious girl"}],
        scene_list=[scene],
    )
    assert script.title == "Test Story"
    assert len(script.scene_list) == 1
    assert isinstance(script.scene_list[0], Scene)
    assert script.scene_list[0].scene_number == 1


def test_graphical_story_generate_video_delegates():
    """Test that generate_video calls the pipeline steps in order."""
    from reweave.workflows.graphical_story_workflow.graphical_story_workflow import GraphicalStoryWorkflow

    workflow = GraphicalStoryWorkflow()

    with patch.object(workflow, 'create_story') as mock_story, \
         patch.object(workflow, 'generate_script') as mock_script, \
         patch.object(workflow, 'generate_footages') as mock_footages, \
         patch.object(workflow, 'generate_final_video') as mock_video:

        workflow.generate_video("test-id", "Test Title", "extra instructions")

        mock_story.assert_called_once_with("test-id", "Test Title", "extra instructions")
        mock_script.assert_called_once_with("test-id")
        mock_footages.assert_called_once_with("test-id")
        mock_video.assert_called_once_with("test-id")


def test_graphical_story_script_builder_imports():
    """Test that ScriptBuilder can be imported."""
    from reweave.workflows.graphical_story_workflow.story_builder import ScriptBuilder
    builder = ScriptBuilder()
    assert builder is not None
