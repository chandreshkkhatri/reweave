"""
Takes in a link to a podcast and creates a summary video of the podcast
"""
from reweave.workflows.final_storytelling_workflows.base_workflow import BaseWorkflow


class PodcastReporterWorkflow(BaseWorkflow):
    """
    Takes podcast and creates a summary of the podcast as a video
    """
    def __init__(self, podcast_link=None):
        self.podcast_link = podcast_link

    def _get_transcript(self):
        """
        Get the transcript of the podcast
        """
        pass
    
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
        pass
    
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