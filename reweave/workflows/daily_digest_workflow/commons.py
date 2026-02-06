from typing import List
from pydantic import BaseModel


class DigestBullet(BaseModel):
    """A single bullet point in the digest."""
    text: str


class DigestScript(BaseModel):
    """Full structured content for a daily digest video."""
    title: str
    bullets: List[DigestBullet]
    narration: str
    image_prompt: str
    caption: str
