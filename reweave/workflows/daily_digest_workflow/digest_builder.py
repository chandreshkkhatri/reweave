"""
Digest Builder

Uses GPT-4 to generate a structured news/topic digest with narration script,
bullet points, image prompt, and social media caption.
"""

import json

from reweave.ai.gemini_service import generate_text
from .commons import DigestScript, DigestBullet


def build_digest(topic):
    """
    Generate a DigestScript for the given topic using GPT-4 function calling.

    Args:
        topic: A topic string like "AI breakthroughs this week".

    Returns:
        A DigestScript instance with title, bullets, narration, image prompt, and caption.
    """
    system_prompt = f"""You are a professional news anchor and content creator specializing in short-form video content.

Given the topic "{topic}", generate content for a 60-second vertical video summary:

1. A catchy title (under 60 characters) that works as a video title.
2. 5-7 concise bullet points covering the most important/interesting aspects of this topic. Each bullet should be 1-2 sentences.
3. A narration script (~120-150 words, approximately 45-50 seconds when spoken) that flows naturally as a voiceover. It should open with a hook, cover the key points conversationally, and end with a brief sign-off.
4. A DALL-E image prompt for a visually striking background image related to the topic. The image should be atmospheric and work well with text overlaid. Do NOT include any text in the image.
5. A social media caption with hashtags (2-3 sentences + 5-8 relevant hashtags).

Make the content engaging, informative, and suitable for a general audience."""

    functions = [
        {
            "name": "create_digest",
            "description": "Creates a structured digest for a short-form video",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Video title, under 60 characters"
                    },
                    "bullets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "A concise bullet point (1-2 sentences)"
                                }
                            },
                            "required": ["text"]
                        },
                        "description": "5-7 key bullet points"
                    },
                    "narration": {
                        "type": "string",
                        "description": "Full narration script, ~120-150 words"
                    },
                    "image_prompt": {
                        "type": "string",
                        "description": "DALL-E prompt for background image. No text."
                    },
                    "caption": {
                        "type": "string",
                        "description": "Social media caption with hashtags"
                    }
                },
                "required": ["title", "bullets", "narration", "image_prompt", "caption"]
            }
        }
    ]

    response = generate_text(
        system_prompt=system_prompt,
        functions=functions,
        function_call={"name": "create_digest"},
        temperature=0.8,
    )

    data = json.loads(response.function_call.arguments)
    return DigestScript(
        title=data["title"],
        bullets=[DigestBullet(**b) for b in data["bullets"]],
        narration=data["narration"],
        image_prompt=data["image_prompt"],
        caption=data["caption"],
    )
