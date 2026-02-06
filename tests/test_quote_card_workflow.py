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


def test_quote_card_workflow_imports():
    """Test that we can import the workflow class."""
    from reweave.workflows.quote_card_workflow import QuoteCardWorkflow
    assert QuoteCardWorkflow is not None


def test_quote_card_workflow_properties():
    """Test workflow name and output dir properties."""
    from reweave.workflows.quote_card_workflow import QuoteCardWorkflow
    workflow = QuoteCardWorkflow()
    assert workflow.workflow_name == "Quote Cards"
    assert workflow.output_dir_prefix == "quote_cards"


def test_quote_card_commons_model():
    """Test the QuoteCard Pydantic model."""
    from reweave.workflows.quote_card_workflow.commons import QuoteCard

    card = QuoteCard(
        quote_text="Test quote",
        attribution="Test Author",
        theme="test",
        image_prompt="A test image",
        caption="Test caption #test",
    )
    assert card.quote_text == "Test quote"
    assert card.attribution == "Test Author"
    assert card.theme == "test"


def test_quote_card_workflow_generate_delegates():
    """Test that generate() passes theme correctly."""
    from reweave.workflows.quote_card_workflow import QuoteCardWorkflow

    workflow = QuoteCardWorkflow()
    with patch.object(workflow, 'generate_quote_card', return_value={"test": True}) as mock:
        result = workflow.generate("test-id", theme="stoic wisdom")
        mock.assert_called_once_with("test-id", "stoic wisdom")
        assert result == {"test": True}


def test_quote_card_workflow_generate_default_theme():
    """Test that generate() uses default theme when none provided."""
    from reweave.workflows.quote_card_workflow import QuoteCardWorkflow

    workflow = QuoteCardWorkflow()
    with patch.object(workflow, 'generate_quote_card', return_value={}) as mock:
        workflow.generate("test-id")
        mock.assert_called_once_with("test-id", "inspiration")
