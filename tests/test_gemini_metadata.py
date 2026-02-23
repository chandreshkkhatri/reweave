import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

def get_metadata_via_gemini(youtube_url):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Simple prompt to ask for metadata
    # We use the same model as transcription for consistency
    model_id = "gemini-2.5-flash"
    
    prompt = "Tell me the exact duration of this video in seconds and its official title. Output ONLY a JSON object with 'title' and 'duration_seconds' keys."
    
    response = client.models.generate_content(
        model=model_id,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(file_uri=youtube_url, mime_type="video/youtube"),
                    types.Part.from_text(text=prompt),
                ]
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    print(f"Gemini Metadata Response: {response.text}")
    return response.text

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=Ukt2gVz25PQ"
    get_metadata_via_gemini(url)
