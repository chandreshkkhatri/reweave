import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reweave.ai.gemini_service import transcribe_youtube_url_chunked

def main():
    load_dotenv()
    
    # Use the long video provided by the user
    test_url = "https://www.youtube.com/watch?v=Rni7Fz7208c" 
    
    print(f"Testing Gemini chunked transcription for: {test_url}")
    print("NOTE: We are hardcoding a 12-minute test duration instead of the full 2 hours to keep the test fast.")
    try:
        # Test just the first 12 minutes (2 chunks of 6 mins each for faster test)
        # Total duration of video is ~2 hours, but we only test a slice here.
        # The actual PodcastVideoGenerator will use the full duration from metadata.
        test_duration = 720 
        chunk_size = 360 # 6 minutes
        
        transcript = transcribe_youtube_url_chunked(test_url, test_duration, chunk_size_seconds=chunk_size)
        
        print("\n--- TRANSCRIPT START ---")
        print(transcript[:1000] + "...") # Show first 1000 chars
        print(f"\n... [Length: {len(transcript)} characters] ...\n")
        print(transcript[-500:]) # Show last 500 chars
        print("--- TRANSCRIPT END ---\n")
        
        # Save to file
        os.makedirs("output", exist_ok=True)
        with open("output/test_transcript.txt", "w") as f:
            f.write(transcript)
        print(f"Transcript saved to: output/test_transcript.txt")
        
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
