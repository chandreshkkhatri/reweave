"""
Clip Assembler

Creates vertical (1080x1920) short-form video clips with:
- Title card (3 seconds)
- Scrolling transcript text
- TTS narration audio
"""

import os

from moviepy import (
    AudioFileClip, ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips,
)

from reweave.utils.video_utils import VERTICAL_WIDTH, VERTICAL_HEIGHT, FPS, DEFAULT_FONT


def _create_title_card(title, duration=3):
    """Create a title card clip with centered text."""
    bg = ColorClip(
        (VERTICAL_WIDTH, VERTICAL_HEIGHT), color=(25, 25, 35), duration=duration
    )
    txt = TextClip(
        font=DEFAULT_FONT,
        text=title,
        font_size=56,
        color='white',
        size=(int(VERTICAL_WIDTH * 0.85), None),
        method='caption',
    ).with_duration(duration).with_position('center')

    return CompositeVideoClip([bg, txt])


def _create_scrolling_content(narration_text, audio_path):
    """Create a scrolling text clip synced to audio duration."""
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    # Add padding for head and tail
    head_delay = 1.5
    tail_delay = 1.5
    total_duration = head_delay + duration + tail_delay

    bg = ColorClip(
        (VERTICAL_WIDTH, VERTICAL_HEIGHT), color=(15, 15, 20), duration=total_duration
    )

    txt = TextClip(
        font=DEFAULT_FONT,
        text=narration_text,
        font_size=36,
        color='white',
        size=(int(VERTICAL_WIDTH * 0.85), None),
        method='caption',
    )

    text_height = txt.h
    x_pos = (VERTICAL_WIDTH - int(VERTICAL_WIDTH * 0.85)) // 2

    def pos(t):
        progress = t / total_duration
        y = int(VERTICAL_HEIGHT - (VERTICAL_HEIGHT + text_height) * progress)
        return (x_pos, y)

    mov = txt.with_position(pos).with_duration(total_duration)
    video = CompositeVideoClip([bg, mov])

    # Attach audio with head delay offset
    audio_with_offset = audio_clip.with_start(head_delay)
    video = video.with_audio(audio_with_offset)

    return video


def assemble_clip(title, narration_text, audio_path, output_path):
    """
    Assemble a single podcast clip video.

    Args:
        title: Topic title for the title card.
        narration_text: Clean narration text for scrolling display.
        audio_path: Path to the TTS narration audio.
        output_path: Path to write the final MP4.

    Returns:
        The output_path.
    """
    title_card = _create_title_card(title)
    content_clip = _create_scrolling_content(narration_text, audio_path)

    final = concatenate_videoclips([title_card, content_clip])

    final.write_videofile(
        output_path, fps=FPS, codec='libx264',
        audio_codec='aac', temp_audiofile=f'temp-clip-audio-{os.getpid()}.m4a',
        remove_temp=True,
    )
    final.close()

    return output_path
