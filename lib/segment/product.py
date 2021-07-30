
class SegmentProduct:
    """An abstract class which models a product to be produced from a segment.
    Subclasses will probably not be used directly, but will support
    SegmentParams.
    """
    export_filename = ""

    def __init__(self, product_params):
        self.params = product_params

    def validate(self):
        """Product-specific validation. Returns a list of errors.
        """
        errors = []
        return errors

    def export(self, export_dir_path, segment_start, segment_end):
        """Exports this product.
        `export_dir_path` should be a pathlib.Path; segment_start and
        segment_end should be datetime.datetime.
        """
        data = self.get_segment_data(segment_start, segment_end)
        self.write_export_file(export_dir_path / self.export_filename, data)

    def get_segment_data(self, segment_start, segment_end):
        """Fetches the data within this time interval.
        """
        raise NotImplemented()

    def write_export_file(self, path, data):
        """Writes `data` to `path` in this export format.
        """
        raise NotImplemented()


class SegmentTranscript(SegmentProduct):
    """An audio transcript in .vtt format.
    """

class SegmentVideo(SegmentProduct):
    """A video in .mp4 format, optionally with an audio track.
    """

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
    'replay_video': SegmentVideo,
    'logs': SegmentLogs,
}
