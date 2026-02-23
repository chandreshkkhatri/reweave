import os
import replicate
from dotenv import load_dotenv

def generate_live_portrait_replicate(source_image_path: str, audio_path: str) -> str:
    """
    Generate a talking-head video using Replicate's API.
    Uses 'lucataco/sadtalker' for stable audio-driven lip-sync.
    """
    load_dotenv()
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        raise ValueError("REPLICATE_API_TOKEN not found in environment")

    os.environ["REPLICATE_API_TOKEN"] = api_token
    
    print(f"Generating Talking Head via Replicate (SadTalker)...")
    print(f"Source Image: {source_image_path}")
    print(f"Audio Path: {audio_path}")
    
    with open(source_image_path, "rb") as image_file, open(audio_path, "rb") as audio_file:
        output = replicate.run(
            "lucataco/sadtalker:85c698db7c0a66d5011435d0191db323034e1da04b912a6d365833141b6a285b",
            input={
                "source_image": image_file,
                "driven_audio": audio_file,
                "still": True,
                "preprocess": "full",
                "enhancer": "gfpgan"
            }
        )
    
    # Replicate returns a URL (or a list of strings if it's multiple outputs)
    if isinstance(output, list):
        return output[0]
    return str(output)
