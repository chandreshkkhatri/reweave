"""
Gemini AI Service

Provides text generation (Gemini), image generation (Imagen 3), and TTS (gTTS)
through a unified interface compatible with the existing workflow patterns.
"""

import json
import os

from google import genai
from google.genai import types
from gtts import gTTS

token = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=token)

DEFAULT_TEXT_MODEL = "gemini-2.5-flash"
DEFAULT_IMAGE_MODEL = "imagen-3.0-generate-002"


# ---------------------------------------------------------------------------
# Response wrapper classes (for compatibility with existing builder patterns)
# ---------------------------------------------------------------------------

class FunctionCallResponse:
    """Wraps a Gemini function call to provide OpenAI-compatible .arguments attr."""
    def __init__(self, name, args_dict):
        self.name = name
        self.arguments = json.dumps(args_dict)


class TextResponse:
    """Wraps a Gemini text response to provide OpenAI-compatible interface."""
    def __init__(self, content=None, function_call=None):
        self.content = content
        self.function_call = function_call


class AudioResponse:
    """Wraps gTTS to provide a .stream_to_file() interface like OpenAI TTS."""
    def __init__(self, text, lang='en'):
        self._tts = gTTS(text=text, lang=lang)

    def stream_to_file(self, path):
        self._tts.save(path)


# ---------------------------------------------------------------------------
# Schema conversion (OpenAI JSON Schema → Gemini types.Schema)
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "object": "OBJECT",
    "string": "STRING",
    "array": "ARRAY",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
}


def _convert_schema(schema):
    """Convert an OpenAI-style JSON Schema dict to a Gemini types.Schema."""
    kwargs = {}
    schema_type = schema.get("type", "object")
    kwargs["type"] = _TYPE_MAP.get(schema_type, schema_type.upper())

    if "description" in schema:
        kwargs["description"] = schema["description"]

    if "properties" in schema:
        kwargs["properties"] = {
            k: _convert_schema(v) for k, v in schema["properties"].items()
        }

    if "required" in schema:
        kwargs["required"] = schema["required"]

    if "items" in schema:
        kwargs["items"] = _convert_schema(schema["items"])

    return types.Schema(**kwargs)


def _convert_functions(functions):
    """Convert OpenAI-style function schemas to Gemini FunctionDeclarations."""
    declarations = []
    for func in functions:
        declarations.append(
            types.FunctionDeclaration(
                name=func["name"],
                description=func.get("description", ""),
                parameters=_convert_schema(func["parameters"]),
            )
        )
    return declarations


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_text(system_prompt, user_prompt=None, model=DEFAULT_TEXT_MODEL,
                  temperature=0.7, functions=None, function_call=None):
    """
    Unified text generation wrapper for Gemini.

    Accepts OpenAI-style function schemas and converts them to Gemini format
    internally, so builder code stays mostly unchanged.

    Args:
        system_prompt: System instruction content.
        user_prompt: Optional user message content.
        model: Gemini model name (default: gemini-2.5-flash).
        temperature: Sampling temperature.
        functions: Optional list of OpenAI-style function schemas.
        function_call: Optional dict like {"name": "func_name"} to force a function call.

    Returns:
        A TextResponse with .content (str) and/or .function_call (.name, .arguments).
    """
    config_kwargs = {
        "temperature": temperature,
        "system_instruction": system_prompt,
    }

    if functions:
        declarations = _convert_functions(functions)
        config_kwargs["tools"] = [types.Tool(function_declarations=declarations)]
        config_kwargs["tool_config"] = types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(mode="ANY")
        )

    response = client.models.generate_content(
        model=model,
        contents=user_prompt or "Please proceed.",
        config=types.GenerateContentConfig(**config_kwargs),
    )

    # Check for function calls in the response
    if response.candidates and response.candidates[0].content:
        for part in response.candidates[0].content.parts:
            if part.function_call:
                fc = part.function_call
                return TextResponse(
                    function_call=FunctionCallResponse(fc.name, dict(fc.args))
                )

    return TextResponse(content=response.text)


def generate_image(prompt):
    """
    Generate an image using Imagen 3.

    Args:
        prompt: Text description of the image to generate.

    Returns:
        Image bytes (PNG/JPEG). Callers should write these directly with
        write_bytes_to_file() instead of downloading from a URL.
    """
    response = client.models.generate_images(
        model=DEFAULT_IMAGE_MODEL,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type='image/png',
        ),
    )

    if response.generated_images:
        return response.generated_images[0].image.image_bytes
    else:
        raise ValueError("No image returned from Imagen API.")


def generate_audio(text, lang='en'):
    """
    Generate TTS audio using Google Text-to-Speech (gTTS).

    Args:
        text: Text to convert to speech.
        lang: Language code (default: 'en').

    Returns:
        An AudioResponse object with a .stream_to_file(path) method,
        compatible with the existing workflow patterns.
    """
    return AudioResponse(text=text, lang=lang)
