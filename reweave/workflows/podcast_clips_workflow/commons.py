from typing import List
from pydantic import BaseModel


class PodcastClip(BaseModel):
    """A single clip extracted from a podcast."""
    clip_number: int
    topic_title: str
    transcript_segment: str
    narration_text: str


class ClipManifest(BaseModel):
    """Manifest of all clips extracted from a podcast."""
    podcast_title: str
    source_url: str
    clips: List[PodcastClip]
