from pathlib import Path
import pandas as pd
from datetime import timedelta
from segment.product.base import SegmentProduct

class SegmentLogs(SegmentProduct):
    """A log file in .csv format.
    When `use_cache` is true, will use a cached subset of the main log file when possible.
    """
    optional_params = [
        "use_cache",
    ]
    main_log_file = "data/df/production.csv"

    def get_segment_data(self):
        """Returns a dataframe 
        """
        if self.params.get("use_cache") and self.get_cached_log_path().exists():
            datapath = self.get_cached_log_path()
        else:
            datapath = self.main_log_file
        df = pd.read_csv(datapath, index_col="timestamp", parse_dates=["timestamp"], low_memory=False)
        df = df.sort_index()
        start, end = self.get_start_end_times()
        df = df.loc[start:end]
        if self.params.get("use_cache") and not self.get_cached_log_path().exists():
            self.get_cached_log_path().parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.get_cached_log_path())
        return df

    def export(self):
        self.get_segment_data().to_csv(self.export_filename())

    def get_cached_log_path(self):
        start, end = self.get_start_end_times()
        return Path("data/cache") / f"logs_{start}-{end}.csv"

    def get_start_end_times(self):
        "Returns (start, end) times"
        start = self.segment_params['start']
        end = start + timedelta(seconds=self.segment_params['duration'])
        return start, end
        

