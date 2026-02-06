"""
Clip Extractor

Uses Gemini to identify the most compelling, standalone segments from a podcast
transcript, suitable for short-form clips.
"""

import json

from reweave.ai.gemini_service import generate_text
from .commons import PodcastClip, ClipManifest


def extract_clips(transcript, podcast_title, source_url, num_clips=5):
    """
    Identify the best clip-worthy segments from a podcast transcript.

    Args:
        transcript: Full podcast transcript text.
        podcast_title: Title of the podcast episode.
        source_url: Original YouTube URL.
        num_clips: Number of clips to extract (default: 5).

    Returns:
        A ClipManifest with the extracted clips.
    """
    system_prompt = f"""You are a social media content editor who specializes in creating viral short-form clips from long podcasts.

Given a podcast transcript, identify the {num_clips} most compelling, self-contained segments that would work as standalone 30-90 second clips for TikTok, Instagram Reels, or YouTube Shorts.

For each clip:
1. Give it a catchy topic title (under 50 characters) that would work as a video title.
2. Extract the relevant transcript segment (the exact text from the transcript).
3. Write a clean, tightened narration version that removes filler words, false starts, and awkward pauses while preserving the meaning and tone. Keep it 50-120 words.

Look for segments that are:
- Surprising or counterintuitive insights
- Practical advice or actionable tips
- Emotionally compelling stories or anecdotes
- Controversial or debate-worthy opinions
- Clear explanations of complex topics"""

    functions = [
        {
            "name": "extract_podcast_clips",
            "description": "Extracts the best clip-worthy segments from a podcast transcript",
            "parameters": {
                "type": "object",
                "properties": {
                    "clips": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "clip_number": {
                                    "type": "integer",
                                    "description": "Sequential clip number starting from 1"
                                },
                                "topic_title": {
                                    "type": "string",
                                    "description": "Catchy title for this clip, under 50 characters"
                                },
                                "transcript_segment": {
                                    "type": "string",
                                    "description": "The exact transcript text for this segment"
                                },
                                "narration_text": {
                                    "type": "string",
                                    "description": "Clean, tightened narration version (50-120 words)"
                                }
                            },
                            "required": ["clip_number", "topic_title", "transcript_segment", "narration_text"]
                        }
                    }
                },
                "required": ["clips"]
            }
        }
    ]

    response = generate_text(
        system_prompt=system_prompt,
        user_prompt=transcript,
        functions=functions,
        function_call={"name": "extract_podcast_clips"},
        temperature=0.7,
    )

    data = json.loads(response.function_call.arguments)
    clips = [PodcastClip(**c) for c in data["clips"]]

    return ClipManifest(
        podcast_title=podcast_title,
        source_url=source_url,
        clips=clips,
    )
