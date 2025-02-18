from inspect import signature
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
from datetime import timedelta
from segment.product.logs import SegmentLogs
from joint_attention import (
    get_location_gaze,
    distance_measure,
    joint_attention_schneider_pea_2013,
    plot_boolean_joint_attention,
)

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
        "use_cache",
        "lookback",
        "plot_filename",
        "distance_threshold",
        "window_seconds",
        "plot_title",
        "palette",
    ]
    default_plot_title = "Joint Visual Attention"
    default_distance_threshold = 6
    default_window_seconds = 2

    def get_start_end_times(self):
        """Overrides this method to account for lookback and window_seconds.
        """
        ws = self.params.get('window_seconds', self.default_window_seconds)
        lookback = max(self.params.get('lookback', 0), ws)
        start = self.segment_params['start'] - timedelta(lookback)
        end = self.segment_params['start'] + timedelta(seconds=self.segment_params['duration'] + ws)
        return start, end

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

    def get_joint_attention_schneider_pea_2013_df(self):
        ws = self.params.get('window_seconds', self.default_window_seconds)
        dt = self.params.get('distance_threshold', self.default_distance_threshold)
        df = self.get_segment_data()
        lgdf = get_location_gaze(df, self.params['players'].values())
        keypairs = list(combinations(self.params['players'].keys(), 2))
        for k0, k1 in keypairs:
            p0 = self.params['players'][k0]
            p1 = self.params['players'][k1]
            col = p0 + '-' + p1
            lgdf[col] = joint_attention_schneider_pea_2013(lgdf, p0, p1, distance_threshold=dt, window_seconds=ws)
        result = self.trim_df(lgdf)
        return result

    def export_joint_attention_schneider_pea_2013(self):
        result = self.get_joint_attention_schneider_pea_2013_df()
        result.to_csv(self.export_filename())
        if self.params.get('plot_filename'):
            figfile = self.export_filename('plot_filename')
            player_name_cols = [self.params['players'][k0] + '-' + self.params['players'][k1] for k0, k1 in keypairs]
            label_cols = [k0 + '-' + k1 for k0, k1 in keypairs]
            result = result[player_name_cols].rename(columns=dict(zip(player_name_cols, label_cols)))
            plt_kwargs = {}
            if self.params.get("palette"):
                colors = sns.color_palette(self.params["palette"]).as_hex()
            else:
                colors = None
            fig = plot_boolean_joint_attention(result, colors)
            plt.title(self.params.get('plot_title', self.default_plot_title))
            plt.ylim([-0.5, len(result.columns) - 0.5])
            fig.savefig(figfile, bbox_inches='tight')

