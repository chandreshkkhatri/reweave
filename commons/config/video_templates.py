"""
Video Templates
"""
from pickle import FALSE
from commons.enums.templates import VideoTemplates
from commons.enums.attributes import Colors, Fonts, Position, TextClipMethod
from commons.classes.dataclasses import VideoTemplate

MAROON_COLOR = [100, 0, 0]
PIANO_CONCERTO_NO_21_C_MAJOR_ANDANTE = "./res/Piano-Concerto-no.-21-in-C-major-K.-467-II.-Andante.mp3"
ALL_I_AM = "./res/audio/All I Am - Dyalla.mp3"
LESLIE = "./res/audio/Leslie's Strut (Sting) - John Deley and the 41 Players.mp3"
TINKER_TIME = "./res/audio/Tinker Time - Nathan Moore.mp3"
DRIVING_BACKWARDS = "./res/audio/Diving in Backwards - Nathan Moore.mp3"

videoTemplates = {}

videoTemplates[VideoTemplates.NIFTY500.value] = VideoTemplate(
    font_color=Colors.WHITE.value,
    font_family=Fonts.AMIRI_REGULAR.value,
    font_size=54,
    title_font_size=72,
    use_background_image=True,
    background_color=MAROON_COLOR,    
    background_image='./commons/resources/frames/Market_Frame_Shorts.png',
    text_clip_method=TextClipMethod.CAPTION.value,
    text_clip_color_pos=Position.CENTER.value,
    background_audio=DRIVING_BACKWARDS,
    terminal_clip_audio=LESLIE,
    title_clip_duration=6,
    end_clip_duration=6,
    subclip_duration=7,
    duration=60,
    aspect_ratio=(900,1600)
    )
videoTemplates[VideoTemplates.CONSTRUCTION.value] = VideoTemplate(
    font_color=Colors.BLACK.value,
    font_family=Fonts.CALIBRI.value,
    font_size=54,
    title_font_size=72,
    use_background_image=True,
    background_color=MAROON_COLOR,    
    background_image='./commons/resources/frames/Construction_Frame.png',
    text_clip_method=TextClipMethod.CAPTION.value,
    text_clip_color_pos=Position.CENTER.value,
    background_audio=TINKER_TIME,
    terminal_clip_audio=LESLIE,
    title_clip_duration=6,
    end_clip_duration=6,
    subclip_duration=7,
    duration=60,
    aspect_ratio=(900,1600)
)

videoTemplates[VideoTemplates.SANSKRITI_1.value] = VideoTemplate(
    font_color=Colors.WHITE.value,
    font_family=Fonts.VERDANA.value,
    font_size=72,
    title_font_size=72,
    use_background_image=True,
    background_image='./res/Sanskriti.png',
    background_color='',
    text_clip_method=TextClipMethod.CAPTION.value,
    text_clip_color_pos=Position.CENTER.value,
    background_audio=PIANO_CONCERTO_NO_21_C_MAJOR_ANDANTE,
    terminal_clip_audio=LESLIE,
    subclip_duration=8,
    duration=60
    )

videoTemplates[VideoTemplates.TEST_TEMPLATE.value] = VideoTemplate(
    font_color=Colors.BLACK.value,
    font_family=Fonts.VERDANA.value,
    font_size=72,
    title_font_size=72,
    use_background_image=True,
    background_image='./res/Anime_Frame.png',
    background_color=MAROON_COLOR,    
    text_clip_method=TextClipMethod.CAPTION.value,
    text_clip_color_pos=Position.CENTER.value,
    background_audio=ALL_I_AM,
    terminal_clip_audio=LESLIE,
    title_clip_duration=6,
    end_clip_duration=6,
    subclip_duration=7,
    duration=60,
    aspect_ratio=(1920,1080)
    )

