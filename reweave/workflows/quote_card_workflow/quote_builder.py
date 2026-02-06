"""
Quote Builder

Uses GPT-4 to generate an inspiring quote, DALL-E image prompt, and social media caption.
"""

import json

from reweave.ai.gemini_service import generate_text
from .commons import QuoteCard


def build_quote_card(theme):
    """
    Generate a QuoteCard for the given theme using GPT-4 function calling.

    Args:
        theme: A theme string like "stoic wisdom" or "monday motivation".

    Returns:
        A QuoteCard instance with quote, attribution, image prompt, and caption.
    """
    system_prompt = f"""You are a creative content producer specializing in inspirational social media content.

Given the theme "{theme}", generate:
1. An inspiring, impactful quote that fits the theme. It can be a famous quote with proper attribution, or an original quote attributed to "Unknown" or a fitting source.
2. A DALL-E image prompt for a beautiful, atmospheric background image that complements the quote. The image should be visually stunning and work well with white text overlaid on it. Do NOT include any text in the image.
3. A social media caption with relevant hashtags (2-3 sentences + 5-8 hashtags).

Make the quote concise (under 200 characters) and memorable."""

    functions = [
        {
            "name": "create_quote_card",
            "description": "Creates a quote card with all necessary content",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote_text": {
                        "type": "string",
                        "description": "The quote itself, under 200 characters"
                    },
                    "attribution": {
                        "type": "string",
                        "description": "Who said/wrote the quote"
                    },
                    "image_prompt": {
                        "type": "string",
                        "description": "DALL-E prompt for a beautiful background image. No text in the image."
                    },
                    "caption": {
                        "type": "string",
                        "description": "Social media caption with hashtags"
                    }
                },
                "required": ["quote_text", "attribution", "image_prompt", "caption"]
            }
        }
    ]

    response = generate_text(
        system_prompt=system_prompt,
        functions=functions,
        function_call={"name": "create_quote_card"},
        temperature=0.9,
    )

    data = json.loads(response.function_call.arguments)
    return QuoteCard(
        quote_text=data["quote_text"],
        attribution=data["attribution"],
        theme=theme,
        image_prompt=data["image_prompt"],
        caption=data["caption"],
    )
