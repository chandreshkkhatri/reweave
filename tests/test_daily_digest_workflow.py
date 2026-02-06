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


def test_daily_digest_workflow_imports():
    """Test that we can import the workflow class."""
    from reweave.workflows.daily_digest_workflow import DailyDigestWorkflow
    assert DailyDigestWorkflow is not None


def test_daily_digest_workflow_properties():
    """Test workflow name and output dir properties."""
    from reweave.workflows.daily_digest_workflow import DailyDigestWorkflow
    workflow = DailyDigestWorkflow()
    assert workflow.workflow_name == "Daily Digest"
    assert workflow.output_dir_prefix == "daily_digest"


def test_daily_digest_commons_models():
    """Test the Pydantic models."""
    from reweave.workflows.daily_digest_workflow.commons import DigestScript, DigestBullet

    bullet = DigestBullet(text="Test bullet point")
    assert bullet.text == "Test bullet point"

    digest = DigestScript(
        title="Test Digest",
        bullets=[bullet],
        narration="Test narration",
        image_prompt="A test image",
        caption="Test caption",
    )
    assert digest.title == "Test Digest"
    assert len(digest.bullets) == 1


def test_daily_digest_workflow_generate_delegates():
    """Test that generate() passes topic correctly."""
    from reweave.workflows.daily_digest_workflow import DailyDigestWorkflow

    workflow = DailyDigestWorkflow()
    with patch.object(workflow, 'generate_digest', return_value={"test": True}) as mock:
        result = workflow.generate("test-id", topic="AI News")
        mock.assert_called_once_with("test-id", "AI News")
        assert result == {"test": True}


def test_daily_digest_workflow_generate_default_topic():
    """Test that generate() uses default topic when none provided."""
    from reweave.workflows.daily_digest_workflow import DailyDigestWorkflow

    workflow = DailyDigestWorkflow()
    with patch.object(workflow, 'generate_digest', return_value={}) as mock:
        workflow.generate("test-id")
        mock.assert_called_once_with("test-id", "technology news")
