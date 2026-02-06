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
sys.modules['yt_dlp'] = MagicMock()
sys.modules['moviepy'] = MagicMock()
sys.modules['youtube_transcript_api'] = MagicMock()

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)


def test_podcast_clips_workflow_imports():
    """Test that we can import the workflow class."""
    from reweave.workflows.podcast_clips_workflow import PodcastClipsWorkflow
    assert PodcastClipsWorkflow is not None


def test_podcast_clips_workflow_properties():
    """Test workflow name and output dir properties."""
    from reweave.workflows.podcast_clips_workflow import PodcastClipsWorkflow
    workflow = PodcastClipsWorkflow()
    assert workflow.workflow_name == "Podcast Highlight Clips"
    assert workflow.output_dir_prefix == "podcast_clips"


def test_podcast_clips_commons_models():
    """Test the Pydantic models."""
    from reweave.workflows.podcast_clips_workflow.commons import PodcastClip, ClipManifest

    clip = PodcastClip(
        clip_number=1,
        topic_title="Test Clip",
        transcript_segment="This is the transcript",
        narration_text="This is the narration",
    )
    assert clip.clip_number == 1
    assert clip.topic_title == "Test Clip"

    manifest = ClipManifest(
        podcast_title="Test Podcast",
        source_url="https://youtube.com/test",
        clips=[clip],
    )
    assert manifest.podcast_title == "Test Podcast"
    assert len(manifest.clips) == 1


def test_podcast_clips_workflow_generate_delegates():
    """Test that generate() passes params correctly."""
    from reweave.workflows.podcast_clips_workflow import PodcastClipsWorkflow

    workflow = PodcastClipsWorkflow()
    with patch.object(workflow, 'generate_clips', return_value={"test": True}) as mock:
        result = workflow.generate("test-id", url="https://youtube.com/test", num_clips=3)
        mock.assert_called_once_with("test-id", "https://youtube.com/test", 3)
        assert result == {"test": True}


def test_podcast_clips_workflow_generate_default_clips():
    """Test that generate() uses default num_clips when none provided."""
    from reweave.workflows.podcast_clips_workflow import PodcastClipsWorkflow

    workflow = PodcastClipsWorkflow()
    with patch.object(workflow, 'generate_clips', return_value={}) as mock:
        workflow.generate("test-id", url="https://youtube.com/test")
        mock.assert_called_once_with("test-id", "https://youtube.com/test", 5)
