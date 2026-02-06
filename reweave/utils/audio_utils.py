"""
Audio Utilities

Helpers for TTS generation of long texts that may exceed API input limits.
"""

import os
import re
import tempfile

from moviepy import AudioFileClip, concatenate_audioclips

from reweave.ai.gemini_service import generate_audio


MAX_TTS_CHARS = 4000


def _split_at_sentences(text, max_chars=MAX_TTS_CHARS):
    """Split text into chunks at sentence boundaries, each under max_chars."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def chunk_and_generate_tts(text, output_path):
    """
    Generate TTS audio for text of any length.

    Splits long text into sentence-boundary chunks, generates TTS for each,
    and concatenates into a single audio file.

    Args:
        text: The text to convert to speech.
        output_path: Path to write the final MP3 file.

    Returns:
        The output_path.
    """
    if len(text) <= MAX_TTS_CHARS:
        audio_stream = generate_audio(text)
        audio_stream.stream_to_file(output_path)
        return output_path

    chunks = _split_at_sentences(text)
    temp_files = []

    try:
        for i, chunk in enumerate(chunks):
            temp_path = os.path.join(
                tempfile.gettempdir(), f"reweave_tts_chunk_{i}.mp3"
            )
            audio_stream = generate_audio(chunk)
            audio_stream.stream_to_file(temp_path)
            temp_files.append(temp_path)

        clips = [AudioFileClip(f) for f in temp_files]
        combined = concatenate_audioclips(clips)
        combined.write_audiofile(output_path)

        for clip in clips:
            clip.close()
        combined.close()
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)

    return output_path
