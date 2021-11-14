from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from segment.product.joint_attention import SegmentJointAttention
from joint_attention import (
    get_location_gaze,
    distance_measure,
    joint_attention_schneider_pea_2013,
    plot_boolean_joint_attention,
)

class SegmentCrossRecurrence(SegmentJointAttention):
    """Returns a cross-recurrence dataframe.
    """
    expected_params = [
        "format",
        "export_filename",
        "players",
    ]
    optional_params = [
        "use_cache",
        "lookback",
        "plot_filename",
        "distance_threshold",
        "plot_title",
        "granularity",
    ]
    default_lookback = 0
    default_plot_title = "Joint Visual Attention"
    default_distance_threshold = 10
    default_granularity = "1s"

    location = "target_block"

    def validate(self):
        errors = super().validate()
        num_players = len(self.params.get("players", []))
        if num_players != 2:
            errors.append("Param 'players' lists {} players but must list two.".format(num_players))
        return errors

    def get_start_end_times(self):
        """Overrides this method to account for lookback and window_seconds.
        """
        lookback = self.params.get('lookback', self.default_lookback)
        start = self.segment_params['start'] - timedelta(lookback)
        end = self.segment_params['start'] + timedelta(seconds=self.segment_params['duration'])
        return start, end

    def export(self):
        df = self.get_segment_data()
        lgdf = get_location_gaze(df, self.params['players'])
        lgdf = lgdf.resample(self.params.get("granularity", self.default_granularity)).first()
        p0, p1 = self.params["players"]
        i, j = np.indices((len(lgdf), len(lgdf)))
        axd2 = {}
        for ax in ['x', 'y', 'z']:
            p0ax = lgdf[f"{p0}_target_block_{ax}"].to_numpy()
            p1ax = lgdf[f"{p1}_target_block_{ax}"].to_numpy()
            axd2[ax] = (p0ax[i] - p1ax[j]) ** 2
        d2 = axd2['x'] + axd2['y'] + axd2['z']            
        dt2 = self.params.get('distance_threshold', self.default_distance_threshold) ** 2
        cross_recurrence = d2 <= dt2

        np.save(self.export_filename(), cross_recurrence)
        if self.params.get("plot_filename"):
            date_format = mdates.DateFormatter('%H:%M')
            extent = mdates.date2num([lgdf.index[0].to_pydatetime(), lgdf.index[-1].to_pydatetime()] * 2)
            f, ax = plt.subplots()
            ax.imshow(cross_recurrence, origin="lower", extent=extent, cmap='Greys', vmin=0, vmax=1)
            ax.xaxis_date()
            ax.yaxis_date()
            ax.xaxis.set_major_formatter(date_format)
            ax.yaxis.set_major_formatter(date_format)
            ax.set_xlabel(p0)
            ax.set_ylabel(p1)
            ax.figure.savefig(self.export_filename("plot_filename"), bbox_inches="tight")



