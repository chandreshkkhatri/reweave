import os
from dotenv import load_dotenv
from reweave.ai.replicate_service import generate_live_portrait_replicate

def test_replicate_liveportrait():
    load_dotenv()
    if not os.getenv("REPLICATE_API_TOKEN"):
        print("Error: REPLICATE_API_TOKEN not found in .env")
        return

    # Use a sample image and driving video
    source_image = "output/full_workflow_test/speaker_portrait.png"
    source_image_path = "output/full_workflow_test/speaker_portrait.png"
    if not os.path.exists(source_image_path):
        print(f"Error: Source image {source_image_path} not found. Please run a full workflow test first or provide a sample image.")
        # Fallback to creating a dummy or using a known URL if possible
        # For a quick test, let's assume the user has a portrait from previous runs
        return

    audio_path = "output/full_workflow_final/summary_audio.mp3" # Use a known or dummy audio path
    
    try:
        print(f"Testing Replicate Talking Head (omni-human) integration...")
        print(f"Generating Talking Head via Replicate...")
        print(f"Source Image: {source_image_path}")
        print(f"Audio Path: {audio_path}")
        
        video_url = generate_live_portrait_replicate(source_image_path, audio_path)
        print(f"Success! Generated video URL: {video_url}")
        
        # Download to verify
        import requests
        output_path = "output/replicate_test_video.mp4"
        print(f"Downloading to {output_path}...")
        resp = requests.get(video_url)
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"Test complete. Video saved to {output_path}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_replicate_liveportrait()
