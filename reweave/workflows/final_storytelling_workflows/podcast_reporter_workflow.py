"""
Takes in a link to a podcast and creates a summary video of the podcast
"""
from youtube_transcript_api import YouTubeTranscriptApi

from reweave.workflows.final_storytelling_workflows.base_workflow import BaseWorkflow
from reweave.ai.openai_service import client

class PodcastReporterWorkflow(BaseWorkflow):
    """
    Takes podcast and creates a summary of the podcast as a video
    """
    def __init__(self, podcast_link=None):
        self.podcast_link = podcast_link
        self.transcript = None
        self.transcript_summary = None

    def _get_transcript(self):
        """
        Get the transcript of the podcast
        """
        self.transcript = YouTubeTranscriptApi.get_transcript(self.podcast_link)
        transcript_string = ' '.join([item['text'] for item in self.transcript])
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",  # You can change the model version if needed
            messages=[{
                "role": "system",  
                "content": f"Summarize the following transcript from youtube video: {transcript_string}"
            }],
        )
        transcript_summary = response.choices[0].message['content']
        self.transcript_summary = transcript_summary
    
    def _get_audio(self):
        """
        Get the audio of the podcast
        """
        pass
    
    def _get_video(self):
        """
        Get the video of the podcast
        """
        pass
    
    def _get_images(self):
        """
        Get the images of the podcast
        """
        pass
    
    def _generate_summary(self):
        """
        Generate a summary of the podcast
        """
        
    
    def _generate_summary_video(self):
        """
        Generate a summary video of the podcast
        """
        pass
    
    def generate_video(self):
        """
        Generate a summary video of the podcast
        """
        self._get_transcript()
        self._get_audio()
        self._get_video()
        self._get_images()
        self._generate_summary()
        self._generate_summary_video()