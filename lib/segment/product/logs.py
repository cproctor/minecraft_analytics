import pandas as pd
from datetime import timedelta
from segment.product.base import SegmentProduct

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

