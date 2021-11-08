import yaml
from pathlib import Path
from datetime import datetime
from subprocess import run
from metadata import get_media_metadata, METADATA_SUFFIX

class SegmentProduct:
    """An abstract class which models a product to be produced from a segment.
    Subclasses will probably not be used directly, but will support
    SegmentParams.
    """
    expected_params = [
        "format",
        "export_filename",
    ]
    optional_params = []

    def __init__(self, segment_params, product_params):
        self.segment_params = segment_params
        self.params = product_params

    def validate(self):
        """Product-specific validation. Returns a list of errors.
        """
        errors = []
        for param in self.expected_params:
            if param not in self.params:
                errors.append("Product {} requires param {}".format(
                    self.__class__.__name__,
                    param
                ))
        for param in self.params:
            if param not in self.expected_params and param not in self.optional_params:
                errors.append("Product {} received unexpected param {}".format(
                    self.__class__.__name__,
                    param
                ))
        return errors

    def export(self):
        """Exports this product.
        """
        raise NotImplemented()

    def export_filename(self):
        """Returns a fully-qualified export filename"""
        export_dir = Path(self.segment_params['export_dir'])
        export_filename = export_dir / self.params['export_filename']
        return export_filename.resolve()

class SegmentTranscript(SegmentProduct):
    """An audio transcript in .vtt format.
    """

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

class SegmentLogs(SegmentProduct):
    """A log file in .csv format.
    """
    main_log_file = "data/df/production.csv"
    export_filename = "server_logs.csv"

    def get_segment_data(self, segment_start, segment_end):
        """Returns a dataframe 
        """
        df = pd.read_csv(main_log_file, index_col="timestamp", parse_dates=["timestamp"])
        return df.loc[segment_start:segment_end]

    def write_export_file(self, path, data):
        """Writes the data (in this case, a pandas dataframe) to disk.
        """
        data.to_csv(path)

PRODUCT_FORMATS = {
    'transcript': SegmentTranscript,
    'video': SegmentVideo,
    'logs': SegmentLogs,
}
