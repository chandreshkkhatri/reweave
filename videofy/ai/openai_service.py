import os
import openai

token = os.getenv("OPENAI_API_KEY")
openai.api_key = token
client = openai.OpenAI(
    api_key=token
)


def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        )

    image_url = response.data[0].url
    
    return image_url


def generate_audio_from_clip(text):
    audio = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
        )
    
    return audio
    
