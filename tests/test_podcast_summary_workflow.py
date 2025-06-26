import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Mock external dependencies before importing our modules
sys.modules['yt_dlp'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['moviepy'] = MagicMock()
sys.modules['moviepy.editor'] = MagicMock()
sys.modules['moviepy.video.fx.speedx'] = MagicMock()

# Ensure project root is on path for imports
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)


def test_podcast_summary_workflow_imports():
    """Test that we can import the workflow class."""
    from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow
    assert PodcastSummaryWorkflow is not None


def test_podcast_summary_workflow_init():
    """Test workflow initialization with mocked dependencies."""
    with patch('reweave.workflows.podcast_summary_workflow.podcast_summary_workflow.PodcastVideoGenerator') as mock_generator:
        from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow

        workflow = PodcastSummaryWorkflow(
            assemblyai_api_key='test_key1', openai_api_key='test_key2')

        # Verify the generator was initialized with correct keys
        mock_generator.assert_called_once_with(
            assemblyai_api_key='test_key1',
            openai_api_key='test_key2'
        )
        assert workflow.generator == mock_generator.return_value


def test_podcast_summary_workflow_generate():
    """Test the generate method delegates to the video generator."""
    with patch('reweave.workflows.podcast_summary_workflow.podcast_summary_workflow.PodcastVideoGenerator') as mock_generator:
        from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow

        # Set up mock return value
        mock_result = {
            'video': 'test_video.mp4',
            'audio': 'test_audio.mp3',
            'transcript': 'test_transcript.txt',
            'summary': 'test_summary.txt',
            'metadata': {'title': 'Test Video'}
        }
        mock_generator.return_value.generate_video_from_url.return_value = mock_result

        workflow = PodcastSummaryWorkflow()
        result = workflow.generate('https://youtube.com/test', 'test_output')

        # Verify the generator method was called with correct arguments
        mock_generator.return_value.generate_video_from_url.assert_called_once_with(
            'https://youtube.com/test', 'test_output'
        )

        # Verify the result is returned unchanged
        assert result == mock_result


def test_podcast_summary_workflow_generate_default_output_dir():
    """Test the generate method uses default output directory."""
    with patch('reweave.workflows.podcast_summary_workflow.podcast_summary_workflow.PodcastVideoGenerator') as mock_generator:
        from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow

        mock_generator.return_value.generate_video_from_url.return_value = {}

        workflow = PodcastSummaryWorkflow()
        workflow.generate('https://youtube.com/test')

        # Verify default output dir is used
        mock_generator.return_value.generate_video_from_url.assert_called_once_with(
            'https://youtube.com/test', 'output'
        )


def test_podcast_summary_workflow_propagates_errors():
    """Test that errors from the video generator are propagated."""
    with patch('reweave.workflows.podcast_summary_workflow.podcast_summary_workflow.PodcastVideoGenerator') as mock_generator:
        from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow

        # Set up mock to raise an error
        mock_generator.return_value.generate_video_from_url.side_effect = RuntimeError(
            "Test error")

        workflow = PodcastSummaryWorkflow()

        with pytest.raises(RuntimeError, match="Test error"):
            workflow.generate('https://youtube.com/test')
