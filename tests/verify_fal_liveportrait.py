import os
from dotenv import load_dotenv
from reweave.workflows.podcast_summary_workflow.podcast_video_generator import PodcastVideoGenerator

def test_liveportrait():
    load_dotenv()
    if not os.getenv("FAL_KEY"):
        print("Error: FAL_KEY not found in .env")
        return

    generator = PodcastVideoGenerator()
    
    # Use a small transcript for speaker image generation
    transcript = """
    Speaker 1 (Elon Musk): Our audience is largely wannabe entrepreneurs in India. 
    And I feel like all of us have so much to learn from you because you've done it so many times over in so many different domains.
    Speaker 2 (Nikhil Kamath): Yeah. Uh, so we will speak to them today and I will try and center all my questions in that direction.
    """
    
    output_dir = "output/test_liveportrait"
    os.makedirs(output_dir, exist_ok=True)
    
    print("Step 1: Generating speaker image...")
    portrait_path = os.path.join(output_dir, "test_portrait.png")
    generator.generate_speaker_image(transcript, portrait_path)
    print(f"Portrait saved to: {portrait_path}")
    
    print("Step 2: Generating LivePortrait video...")
    video_path = os.path.join(output_dir, "test_liveportrait.mp4")
    audio_path = "output/test_transcript.txt" # Dummy path, not used for lip sync in this simple test
    
    # We use the default driving video internal to the method
    generator.create_liveportrait_video(portrait_path, audio_path, video_path)
    print(f"Video saved to: {video_path}")
    
    print("Success! Verification complete.")

if __name__ == "__main__":
    test_liveportrait()
