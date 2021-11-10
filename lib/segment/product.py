import yaml
from pathlib import Path
from datetime import datetime
from subprocess import run
from datetime import timedelta
from inspect import signature
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt
from metadata import get_media_metadata, METADATA_SUFFIX
from joint_attention import (
    get_location_gaze,
    distance_measure,
    joint_attention_schneider_pea_2013,
    plot_boolean_joint_attention,
)

class SegmentProduct:
    """An abstract class which models a product to be produced from a segment.
    Required methods are validate and export.
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

    def export_filename(self, filename_key='export_filename'):
        """Returns a fully-qualified export filename"""
        export_dir = Path(self.segment_params['export_dir'])
        export_filename = export_dir / self.params[filename_key]
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
    # TEMP for efficiency while testing, you can cache a smaller df
    #main_log_file = "log_slice_temp.csv"
    main_log_file = "data/df/production.csv"

    def get_segment_data(self):
        """Returns a dataframe 
        """
        df = pd.read_csv(self.main_log_file, index_col="timestamp", parse_dates=["timestamp"])
        df = df.sort_index()
        start = self.segment_params['start']
        end = start + timedelta(seconds=self.segment_params['duration'])
        return df.loc[start:end]

    def export(self):
        self.get_segment_data().to_csv(self.export_filename())

class SegmentJointAttention(SegmentLogs):
    """Returns a joint attention dataframe. 
    Param `players` should be a dict mapping desired keys (e.g. 'a') to usernames
    Optional param `lookback` will look back this many seconds for initial position and
    gaze values
    """
    expected_params = [
        "format",
        "export_filename",
        "players",
        "measure",
    ]
    optional_params = [
        "lookback",
        "plot_filename",
        "distance_threshold",
        "window_seconds",
        "plot_title",
    ]
    default_plot_title = "Joint Visual Attention"

    def get_location_gaze(self, lookback=0, lookahead=0):
        """Returns a location gaze df for the specified players.
        When lookback or lookahead are provided, extends the selection window.
        """
        df = pd.read_csv(self.main_log_file, index_col="timestamp", parse_dates=["timestamp"])
        df = df.sort_index()
        start = self.segment_params['start'] - timedelta(seconds=lookback)
        end = (
            self.segment_params['start'] + 
            timedelta(seconds=self.segment_params['duration']) + 
            timedelta(seconds=lookahead)
        )
        df = df.loc[start:end]
        lgdf = get_location_gaze(df, self.params['players'])
        return lgdf

    def trim_df(self, df):
        """Trims a df to start and end (start+duration) times defined in segment.
        Sometimes this should be done after initial selection because lookback 
        or lookahead is included.
        """
        start = self.segment_params['start']
        end = start + timedelta(seconds=self.segment_params['duration'])
        return df.loc[start:end]

    def export(self):
        if self.params['measure'] == "joint_attention_schneider_pea_2013":
            self.export_joint_attention_schneider_pea_2013()
        else:
            raise ValueError("Unsupported measure: {}".format(self.params['measure']))

    def export_joint_attention_schneider_pea_2013(self):
        default_ws = signature(joint_attention_schneider_pea_2013).parameters['window_seconds'].default
        ws = self.params.get('window_seconds', default_ws)
        lookback = max(self.params.get('lookback', 0), ws)
        lookahead = ws
        lgdf = self.get_location_gaze(lookback=lookback, lookahead=lookahead)
        keypairs = list(combinations(self.params['players'].keys(), 2))
        for a, b in keypairs:
            lgdf[a + '-' + b] = joint_attention_schneider_pea_2013(lgdf, a, b, 
                    distance_threshold=self.params.get('distance_threshold'), window_seconds=ws)
        result = lgdf[[a + '-' + b for a, b in keypairs]]
        result = self.trim_df(result)
        result.to_csv(self.export_filename())
        if self.params.get('plot_filename'):
            figfile = self.export_filename('plot_filename')
            fig = plot_boolean_joint_attention(result)
            plt.title(self.params.get('plot_title', self.default_plot_title))
            plt.ylim([-0.5, len(result.columns) - 0.5])
            fig.savefig(figfile, bbox_inches='tight')

PRODUCT_FORMATS = {
    'transcript': SegmentTranscript,
    'video': SegmentVideo,
    'logs': SegmentLogs,
    'joint_attention': SegmentJointAttention,
}
