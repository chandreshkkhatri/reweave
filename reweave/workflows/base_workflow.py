"""
Base Workflow

Abstract base class for all content creation workflows in Reweave.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseWorkflow(ABC):
    """Abstract base for all content creation workflows."""

    @abstractmethod
    def generate(self, content_id: str, **kwargs) -> Dict[str, Any]:
        """Run the full pipeline and return paths to generated outputs."""
        ...

    @property
    @abstractmethod
    def workflow_name(self) -> str:
        """Human-readable workflow name for CLI and logging."""
        ...

    @property
    @abstractmethod
    def output_dir_prefix(self) -> str:
        """Base output directory name (e.g., 'daily_digest')."""
        ...
