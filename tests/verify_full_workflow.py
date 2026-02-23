import os
import shutil
from dotenv import load_dotenv
from reweave.workflows.podcast_summary_workflow.podcast_summary_workflow import PodcastSummaryWorkflow

def test_full_workflow():
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY not found in .env")
        return
    if not os.getenv("FAL_KEY"):
        print("Error: FAL_KEY not found in .env")
        return

    workflow = PodcastSummaryWorkflow()
    
    # Use the specific video provided by the user for the test
    youtube_url = "https://www.youtube.com/watch?v=Ukt2gVz25PQ" 
    output_dir = "output/full_workflow_test"
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting full workflow test for: {youtube_url}")
    print(f"Outputs will be saved to: {output_dir}")
    
    try:
        # Test speaker customization
        speaker_desc = "a professional middle-aged south indian woman with glasses and short hair"
        print(f"Using custom speaker description: {speaker_desc}")
        
        result = workflow.generate(
            youtube_url=youtube_url,
            output_dir=output_dir,
            use_audio_transcription=True,
            speaker_description=speaker_desc
        )
        
        print("\n--- Workflow Result ---")
        for key, value in result.items():
            if key != "metadata":
                print(f"{key}: {value}")
                if not os.path.exists(str(value)):
                    print(f"WARNING: File {value} does not exist!")
        
        print("\nSuccess! Full workflow verification complete.")
        
    except Exception as e:
        print(f"\nError during workflow execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
