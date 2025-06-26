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

    if response.data and len(response.data) > 0 and hasattr(response.data[0], "url"):
        image_url = response.data[0].url
        return image_url
    else:
        raise ValueError("No image URL returned from OpenAI API.")


def generate_audio(text):
    audio = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )

    return audio
