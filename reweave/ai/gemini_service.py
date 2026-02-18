"""
Gemini AI Service

Provides text generation (Gemini), image generation (Imagen 3), and TTS (Gemini native TTS)
through a unified interface compatible with the existing workflow patterns.
"""

import io
import json
import os
import struct

from google import genai
from google.genai import types

DEFAULT_TEXT_MODEL = "gemini-2.5-flash"
DEFAULT_IMAGE_MODEL = "gemini-3-pro-image-preview"
FALLBACK_IMAGE_MODEL = "imagen-4.0-fast-generate-001"
DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"

_client = None


def _get_client():
    """Lazily initialize the Gemini client on first API call."""
    global _client
    if _client is None:
        token = os.getenv("GEMINI_API_KEY")
        if not token:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set. "
                "Set it in your .env file or export it in your shell."
            )
        _client = genai.Client(api_key=token)
    return _client


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
    """Wraps raw PCM bytes and converts to MP3 via pydub on stream_to_file()."""
    def __init__(self, pcm_bytes: bytes, sample_rate: int = 24000, channels: int = 1):
        self._pcm_bytes = pcm_bytes
        self._sample_rate = sample_rate
        self._channels = channels

    def stream_to_file(self, path: str):
        from pydub import AudioSegment
        audio = AudioSegment(
            data=self._pcm_bytes,
            sample_width=2,          # 16-bit PCM
            frame_rate=self._sample_rate,
            channels=self._channels,
        )
        audio.export(path, format="mp3")


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

    response = _get_client().models.generate_content(
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
    Generate an image using the configured image model, with automatic fallback
    to FALLBACK_IMAGE_MODEL on 503 UNAVAILABLE errors.

    Args:
        prompt: Text description of the image to generate.

    Returns:
        Image bytes (PNG/JPEG).
    """
    from google.genai.errors import ServerError

    client = _get_client()
    try:
        return _generate_image_with_model(client, DEFAULT_IMAGE_MODEL, prompt)
    except ServerError as e:
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            print(f"Primary model unavailable, falling back to {FALLBACK_IMAGE_MODEL}...")
            return _generate_image_with_model(client, FALLBACK_IMAGE_MODEL, prompt)
        raise


def _generate_image_with_model(client, model, prompt):
    """Generate an image with a specific model, routing by model family."""
    if model.startswith("gemini-"):
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data
        raise ValueError("No image returned from Gemini image model.")

    # Imagen models
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            output_mime_type='image/png',
            negative_prompt="text, letters, words, captions, titles, subtitles, labels, watermarks, speech bubbles, thought bubbles, signs with text",
        ),
    )
    if response.generated_images:
        return response.generated_images[0].image.image_bytes
    raise ValueError("No image returned from Imagen API.")


def transcribe_audio(audio_path, model=DEFAULT_TEXT_MODEL):
    """
    Transcribe an audio file using Gemini's multimodal audio understanding.

    Uses the File API for reliable handling of large audio files (podcasts, etc.).

    Args:
        audio_path: Path to the audio file (mp3, m4a, wav, etc.).
        model: Gemini model name (default: gemini-2.5-flash).

    Returns:
        Transcription text as a string.
    """
    client = _get_client()
    uploaded_file = client.files.upload(file=audio_path)
    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                uploaded_file,
                'Transcribe this audio accurately and completely. '
                'Include all spoken words. If multiple languages are spoken '
                '(e.g. Hindi and English), transcribe each in its original language. '
                'Output only the transcription text, no timestamps or labels.',
            ],
            config=types.GenerateContentConfig(temperature=0.1),
        )
        return response.text
    finally:
        client.files.delete(name=uploaded_file.name)


def generate_audio(text, lang='en'):
    """
    Generate TTS audio using Gemini native TTS for natural, expressive speech.

    Falls back to gTTS if the Gemini TTS model is unavailable.

    Args:
        text: Text to convert to speech.
        lang: Language code (currently used only for gTTS fallback).

    Returns:
        An AudioResponse object with a .stream_to_file(path) method.
    """
    from google.genai.errors import ServerError, ClientError

    try:
        client = _get_client()
        response = client.models.generate_content(
            model=DEFAULT_TTS_MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Charon",
                        )
                    )
                ),
            ),
        )
        pcm_bytes = response.candidates[0].content.parts[0].inline_data.data
        return AudioResponse(pcm_bytes=pcm_bytes, sample_rate=24000, channels=1)
    except (ServerError, ClientError, Exception) as e:
        print(f"Gemini TTS unavailable ({e}), falling back to gTTS...")
        from gtts import gTTS
        import io

        class _GTTSFallback:
            def __init__(self, text, lang):
                self._tts = gTTS(text=text, lang=lang)
            def stream_to_file(self, path):
                self._tts.save(path)

        return _GTTSFallback(text, lang)
