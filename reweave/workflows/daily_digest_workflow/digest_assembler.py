"""
Digest Video Assembler

Creates a vertical (1080x1920) video with:
- Hero image as background with dark overlay
- Title text at the top
- Bullet points appearing one-by-one, timed evenly across the narration
- TTS audio track
"""

import os

from moviepy import ImageClip, TextClip, ColorClip, CompositeVideoClip, AudioFileClip

from reweave.utils.video_utils import VERTICAL_WIDTH, VERTICAL_HEIGHT, FPS, DEFAULT_FONT


def assemble_digest_video(image_path, audio_path, title, bullets, output_path):
    """
    Assemble a vertical digest video.

    Args:
        image_path: Path to the background image.
        audio_path: Path to the TTS narration MP3.
        title: Video title string.
        bullets: List of bullet point strings.
        output_path: Path to write the final MP4.

    Returns:
        The output_path.
    """
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration + 4  # 2s intro + 2s outro padding

    # Background image (stretched to vertical)
    bg_image = (
        ImageClip(image_path)
        .resized((VERTICAL_WIDTH, VERTICAL_HEIGHT))
        .with_duration(total_duration)
    )

    # Dark overlay for readability
    overlay = (
        ColorClip((VERTICAL_WIDTH, VERTICAL_HEIGHT), color=(0, 0, 0))
        .with_opacity(0.55)
        .with_duration(total_duration)
    )

    clips = [bg_image, overlay]

    # Title card (appears at top, visible throughout)
    title_clip = (
        TextClip(
            font=DEFAULT_FONT,
            text=title,
            font_size=52,
            color='white',
            size=(int(VERTICAL_WIDTH * 0.85), None),
            method='caption',
        )
        .with_position(('center', 180))
        .with_start(0)
        .with_duration(total_duration)
    )
    clips.append(title_clip)

    # Decorative line under title
    line_clip = (
        ColorClip((int(VERTICAL_WIDTH * 0.6), 3), color=(255, 255, 255))
        .with_position(('center', 280))
        .with_start(0)
        .with_duration(total_duration)
        .with_opacity(0.6)
    )
    clips.append(line_clip)

    # Bullet points — appear one by one, evenly timed
    bullet_start_time = 2.0  # Start after title settles
    bullet_area_duration = total_duration - bullet_start_time - 1.5
    time_per_bullet = bullet_area_duration / max(len(bullets), 1)

    y_start = 350
    y_spacing = 130

    for i, bullet_text in enumerate(bullets):
        start_t = bullet_start_time + i * time_per_bullet
        remaining = total_duration - start_t

        # Bullet marker
        marker_clip = (
            TextClip(
                font=DEFAULT_FONT,
                text="•",
                font_size=36,
                color='#4FC3F7',
            )
            .with_position((60, y_start + i * y_spacing))
            .with_start(start_t)
            .with_duration(remaining)
        )
        clips.append(marker_clip)

        # Bullet text
        text_clip = (
            TextClip(
                font=DEFAULT_FONT,
                text=bullet_text,
                font_size=32,
                color='white',
                size=(int(VERTICAL_WIDTH * 0.75), None),
                method='caption',
            )
            .with_position((110, y_start + i * y_spacing))
            .with_start(start_t)
            .with_duration(remaining)
        )
        clips.append(text_clip)

    # Compose video
    video = CompositeVideoClip(clips, size=(VERTICAL_WIDTH, VERTICAL_HEIGHT))

    # Add audio starting after 2-second intro
    audio_with_offset = audio_clip.with_start(2.0)
    video = video.with_audio(audio_with_offset)

    video.write_videofile(
        output_path, fps=FPS, codec='libx264',
        audio_codec='aac', temp_audiofile='temp-digest-audio.m4a',
        remove_temp=True,
    )
    video.close()
    audio_clip.close()

    return output_path
