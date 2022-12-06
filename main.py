"""
Main
"""
from src.commons.enums import ClipType
from src.flask_app.controllers import main_controller

if __name__ == '__main__':
    main_controller.create_video_file()
