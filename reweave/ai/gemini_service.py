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


def transcribe_youtube_url(youtube_url, model=DEFAULT_TEXT_MODEL, start_offset=None, end_offset=None, context=None):
    """
    Transcribe a YouTube video directly using Gemini's native YouTube support.

    Args:
        youtube_url: The public YouTube URL.
        model: Gemini model name (default: gemini-2.5-flash).
        start_offset: Optional start time in seconds.
        end_offset: Optional end time in seconds.
        context: Optional context string to help with transcription (e.g. previous chunk summary).

    Returns:
        Transcription text as a string.
    """
    client = _get_client()
    
    video_metadata = None
    if start_offset is not None or end_offset is not None:
        video_metadata = types.VideoMetadata(
            start_offset=f"{int(start_offset)}s" if start_offset is not None else None,
            end_offset=f"{int(end_offset)}s" if end_offset is not None else None,
        )

    prompt = (
        'Transcribe this YouTube video accurately and completely. '
        'Identify all speakers and label their dialogues (e.g., "Speaker 1:", "Speaker 2:" or names like "Elon Musk:" if identifiable). '
        'Include all spoken words. '
    )
    if context:
        prompt += f'Context from previous part (use the same speaker labels if possible): {context}\n\n'
    prompt += 'Output only the transcription text with speaker labels, no timestamps.'

    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part(
                file_data=types.FileData(
                    file_uri=youtube_url,
                    mime_type='video/youtube'
                ),
                video_metadata=video_metadata
            ),
            prompt,
        ],
        config=types.GenerateContentConfig(temperature=0.1),
    )
    return response.text


def transcribe_youtube_url_chunked(youtube_url, total_duration, chunk_size_seconds=600, model=DEFAULT_TEXT_MODEL):
    """
    Transcribe a long YouTube video by breaking it into smaller chunks.

    Args:
        youtube_url: The public YouTube URL.
        total_duration: Total duration of the video in seconds.
        chunk_size_seconds: Duration of each chunk in seconds (default: 10 minutes).
        model: Gemini model name.

    Returns:
        Combined transcription text.
    """
    num_chunks = (int(total_duration) // chunk_size_seconds) + (1 if int(total_duration) % chunk_size_seconds > 0 else 0)
    full_transcript = []
    
    print(f"Dividing video into {num_chunks} chunks of {chunk_size_seconds}s each...")
    
    context = None
    for i in range(num_chunks):
        start = i * chunk_size_seconds
        end = min((i + 1) * chunk_size_seconds, int(total_duration))
        
        print(f"Transcribing chunk {i+1}/{num_chunks} ({start}s to {end}s)...")
        # Add a simple retry for transient server errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                chunk_text = transcribe_youtube_url(youtube_url, model=model, start_offset=start, end_offset=end, context=context)
                full_transcript.append(chunk_text)
                break
            except Exception as e:
                if attempt < max_retries:
                    print(f"  Chunk transcription failed (attempt {attempt+1}): {e}. Retrying...")
                    import time
                    time.sleep(2)
                else:
                    print(f"  Chunk transcription failed after {max_retries+1} attempts.")
                    raise e
        
        # Get a small context for the next chunk if there's more to go
        if i < num_chunks - 1:
            try:
                summary_prompt = "Summarize the last few sentences of this transcription segment to provide context for the next part."
                context_resp = generate_text(
                    system_prompt=summary_prompt,
                    user_prompt=chunk_text[-2000:], # Use last part for context
                    temperature=0.3
                )
                context = context_resp.content
            except Exception:
                context = None
                
    return "\n".join(full_transcript)


def get_youtube_metadata_gemini(youtube_url: str) -> dict:
    """
    Extract YouTube video metadata (title, duration) using Gemini API.
    This is more reliable than yt-dlp in restricted environments.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = (
        "Tell me the exact duration of this video in seconds and its official title. "
        "Output ONLY a JSON object with 'title' and 'duration_seconds' keys."
    )
    
    try:
        response = client.models.generate_content(
            model=DEFAULT_TEXT_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(file_uri=youtube_url, mime_type="video/youtube"),
                        types.Part.from_text(text=prompt),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                # Use JSON schema for structured output if possible, or just MIME type
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        return {
            'title': data.get('title', 'Unknown Title'),
            'duration': data.get('duration_seconds', 0),
            'uploader': 'Unknown',
            'description': ''
        }
    except Exception as e:
        print(f"Gemini metadata extraction failed: {e}")
        raise e


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


def generate_subtitles(text: str, total_duration: float) -> str:
    """
    Generate SRT subtitles for the given text, scaled to the total duration.
    Uses Gemini to segment the text into natural-sounding chunks.
    """
    client = _get_client()
    system_prompt = (
        "Split the following text into natural, readable subtitle segments. "
        "For each segment, provide the text and a relative weight (0-1) for how much of the "
        "total duration it should occupy based on word count/complexity. "
        "Output ONLY a JSON array of objects: [{'text': '...', 'weight': 0.1}, ...]"
    )
    
    try:
        response = client.models.generate_content(
            model=DEFAULT_TEXT_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=system_prompt),
                        types.Part.from_text(text=text),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        segments = json.loads(response.text)
        
        # Scale weights to ensure they sum to 1.0
        total_weight = sum(s.get('weight', 0) for s in segments)
        if total_weight == 0:
            total_weight = len(segments)
            for s in segments:
                s['weight'] = 1.0
                
        srt_lines = []
        current_time = 0.0
        
        for i, s in enumerate(segments):
            segment_duration = (s['weight'] / total_weight) * total_duration
            start_time = current_time
            end_time = current_time + segment_duration
            
            # Format as SRT timestamp: HH:MM:SS,ms
            def format_ts(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                sec = int(seconds % 60)
                ms = int((seconds % 1) * 1000)
                return f"{h:02}:{m:02}:{sec:02},{ms:03}"
            
            srt_lines.append(str(i + 1))
            srt_lines.append(f"{format_ts(start_time)} --> {format_ts(end_time)}")
            srt_lines.append(s['text'])
            srt_lines.append("")
            
            current_time = end_time
            
        return "\n".join(srt_lines)
    except Exception as e:
        print(f"Subtitle generation failed: {e}")
        # Simplistic fallback if AI fails
        return f"1\n00:00:00,000 --> 00:00:05,000\n{text[:100]}..."


def get_visual_keywords(text: str, num_keywords: int = 5) -> list:
    """Ask Gemini to pick key visual topics for image generation."""
    client = _get_client()
    prompt = (
        f"Based on the following summary, pick {num_keywords} distinct visual themes or "
        "descriptors that would make for compelling images in a slideshow. "
        "Output ONLY a JSON array of short, descriptive strings."
    )
    
    try:
        response = client.models.generate_content(
            model=DEFAULT_TEXT_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_text(text=text),
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Visual keyword extraction failed: {e}")
        return ["A professional podcast studio recording setting."]
