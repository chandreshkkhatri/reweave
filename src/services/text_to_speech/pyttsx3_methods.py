import pyttsx3
engine = pyttsx3.init()


def save_audio(text, filename):
    engine.setProperty('voice', 'english')
    engine.save_to_file(text, filename)
    engine.runAndWait()
