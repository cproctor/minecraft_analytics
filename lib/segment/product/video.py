from datetime import datetime
from subprocess import run
from pathlib import Path
from segment.product.base import SegmentProduct
from metadata import get_media_metadata, METADATA_SUFFIX

class SegmentVideo(SegmentProduct):
    """A video in .mp4 format, optionally with an audio track.
    """
    expected_params = [
        "format",
        "export_filename",
        "video_source",
    ]
    optional_params = [
        "audio_source"
    ]

    def export(self):
        if "audio_source" in self.params:
            export_file = self.merge_audio_and_video()
        else:
            export_file = self.trim_video()

    def merge_audio_and_video(self):
        """Merges an audio and a video file. 
        Assumes the video has no existing audio.     
        See https://superuser.com/questions/277642/how-to-merge-audio-and-video-file-in-ffmpeg
        """
        cmd = 'ffmpeg -v quiet -ss {} -t {} -i "{}" -ss {} -t {} -i "{}" -c copy "{}"'
        video_start_time = self.get_media_relative_start_time(self.params['video_source'])
        audio_start_time = self.get_media_relative_start_time(self.params['audio_source'])
        command = cmd.format(
            video_start_time,
            self.segment_params['duration'],
            self.params['video_source'],
            audio_start_time,
            self.segment_params['duration'],
            self.params['audio_source'],
            self.export_filename(),
        )
        run(command, shell=True)

    def trim_video(self):
        """Trims a video"""
        cmd = 'ffmpeg -v quiet -ss {} -t {} -i "{}" -c copy "{}"'
        video_start_time = self.get_media_relative_start_time(self.params['video_source'])
        command = cmd.format(
            video_start_time,
            self.segment_params['duration'],
            self.params['video_source'],
            self.export_filename(),
        )
        run(command, shell=True)

    def get_media_relative_start_time(self, source_path):
        """Returns the media's relative start time as HH:MM:SS. 
        """
        source_path = Path(source_path)
        metadata_path = source_path.parent / (source_path.name + METADATA_SUFFIX)
        md = get_media_metadata(metadata_path)
        return self.segment_params['start'] - md['start'].astype(datetime)

