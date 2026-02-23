import os
import fal_client
from dotenv import load_dotenv

load_dotenv()

def generate_live_portrait(source_image_url: str, audio_path: str = None, driving_video_url: str = None) -> str:
    """
    Generate a talking-head video using fal.ai.
    Uses 'fal-ai/echomimic-v3' for audio-driven animation if audio_path is provided.
    Otherwise falls back to 'fal-ai/live-portrait' with a driving video.
    """
    def on_queue_update(update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                print(f"fal.ai: {log['message']}")

    # Handle local files by uploading them
    if os.path.exists(source_image_url):
        print(f"Uploading local image: {source_image_url}")
        source_image_url = fal_client.upload_file(source_image_url)
    
    if audio_path and os.path.exists(audio_path):
        print(f"Uploading local audio: {audio_path}")
        audio_url = fal_client.upload_file(audio_path)
        
        print("Using fal-ai/longcat-single-avatar/image-audio-to-video (long-duration talking head)...")
        result = fal_client.subscribe(
            "fal-ai/longcat-single-avatar/image-audio-to-video",
            arguments={
                "image_url": source_image_url,
                "audio_url": audio_url,
                "resolution": "480p", # Faster than 720p
                "num_segments": 1, # Default
                "audio_guidance_scale": 4.0
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
    else:
        if driving_video_url and os.path.exists(driving_video_url):
            print(f"Uploading local driving video: {driving_video_url}")
            driving_video_url = fal_client.upload_file(driving_video_url)
        elif driving_video_url is None:
            driving_video_url = "https://storage.googleapis.com/falserverless/model_tests/live-portrait/liveportrait-example.mp4"

        print("Using fal-ai/live-portrait (video-driven)...")
        result = fal_client.subscribe(
            "fal-ai/live-portrait",
            arguments={
                "image_url": source_image_url,
                "video_url": driving_video_url,
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
    
    # Return the video URL from result
    if result.get('video_url'):
        return result['video_url']
    elif result.get('video'):
        return result['video'].get('url')
    return result.get('url')
