from commons.config.video_templates import videoTemplates
from src.commons.classes.dataclasses import VideoTemplate


def get_template(template: str) -> VideoTemplate:
    for key, value in videoTemplates.items():
        if key == template:
            return value
    return None
