"""
This file contains helper functions for the core builder
"""
from app.models.VideoTemplate import VideoTemplateModel, VideoTemplateCrudModel
from app.commons.config import config
from app.commons.classes.dataclasses import VideoTemplate
from app.commons.enums.attributes import Colors

MAROON_COLOR = [100, 0, 0]
AUDIO_DIR = f"{config.RESOURCES_DIR}/assets/audio"
PIANO_CONCERTO_NO_21_C_MAJOR_ANDANTE = f"{AUDIO_DIR}/Piano-Concerto-no.-21-in-C-major-K.-467-II.-Andante.mp3"
ALL_I_AM = f"{AUDIO_DIR}/All I Am - Dyalla.mp3"
LESLIE = f"{AUDIO_DIR}/Leslie's Strut (Sting) - John Deley and the 41 Players.mp3"
TINKER_TIME = f"{AUDIO_DIR}/Tinker Time - Nathan Moore.mp3"
DRIVING_BACKWARDS = f"{AUDIO_DIR}/Diving in Backwards - Nathan Moore.mp3"
MARKET_FRAME_SHORTS = f"{config.RESOURCES_DIR}/assets/Frames/Market_Frame_Shorts.png"


async def get_template(name: str) -> VideoTemplate:
    video_template_crud_model = VideoTemplateCrudModel()
    template = await video_template_crud_model.get_by_name(name)
    if template:
        del template['name']
        template = VideoTemplateModel.parse_obj(template)
        template.font_color = get_color(template.font_color)
        template.background_image = get_image(template.background_image)
        template.background_color = get_bg_color(template.background_color)
        template.background_audio = get_audio(template.background_audio)
        template.terminal_clip_audio = get_terminal_audio(
            template.terminal_clip_audio)
        template.aspect_ratio = get_aspect_ratio(template.aspect_ratio)
        del template.id

        return VideoTemplate(**template.__dict__)


def get_color(color: str) -> str:
    return Colors[color].value


def get_image(image: str) -> str:
    return f"{config.RESOURCES_DIR}/assets/Frames/{image}"


def get_bg_color(color: str) -> list:
    if color == 'Maroon':
        return [100, 0, 0]
    return [0, 0, 0]


def get_audio(audio: str) -> str:
    if audio == 'ALL_I_AM':
        return ALL_I_AM


def get_terminal_audio(audio: str) -> str:
    if audio == 'LESLIE':
        return LESLIE


def get_aspect_ratio(aspect_ratio: str) -> tuple:
    if aspect_ratio == 'shorts':
        return (900, 1600)
    return (1600, 900)


def get_cover_image(cover_image: str) -> str:
    return f"{config.RESOURCES_DIR}/assets/Covers/{cover_image}"
