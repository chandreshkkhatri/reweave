from commons.config.video_templates import videoTemplates


def get_template(template: str):
    for key, value in videoTemplates.items():
        if key == template:
            return value
    return None
