from subprocess import run
from segment.product.base import SegmentProduct

class SegmentAudio(SegmentProduct):
    """An audio file in m4a format"""

    expected_params = [
        "format",
        "export_filename",
        "audio_source",
    ]

    def export(self):
        cmd = 'ffmpeg -v quiet -ss {} -t {} -i "{}" -c copy "{}"'
        start_time = self.get_media_relative_start_time(self.params['audio_source'])
        command = cmd.format(
            start_time,
            self.segment_params['duration'],
            self.params['audio_source'],
            self.export_filename(),
        )
        print(command)
        run(command, shell=True, check=True)
    
