from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from segment.product.joint_attention import SegmentJointAttention
from segment.product.cross_recurrence import SegmentCrossRecurrence
from joint_attention import (
    get_location_gaze,
    distance_measure,
    joint_attention_schneider_pea_2013,
    plot_boolean_joint_attention,
)

class SegmentCrossRecurrenceAugmented(SegmentCrossRecurrence):
    """Returns a cross-recurrence dataframe.
    """
    expected_params = [
        "format",
        "export_filename",
        "block_action_filename",
        "players",
    ]

    def export(self):
        df = self.get_segment_data()
        lgdf = get_location_gaze(df, self.params['players'])
        lgdf = lgdf.resample(self.params.get("granularity", self.default_granularity)).first()
        #badf = self.get_block_action_df(df)
        (player_label0, player0), (player_label1, player1) = self.params["players"].items()
        i, j = np.indices((len(lgdf), len(lgdf)))
        axd2 = {}
        for ax in ['x', 'y', 'z']:
            p0ax = lgdf[f"{player_label0}_target_block_{ax}"].to_numpy()
            p1ax = lgdf[f"{player_label1}_target_block_{ax}"].to_numpy()
            axd2[ax] = (p0ax[i] - p1ax[j]) ** 2
        d2 = axd2['x'] + axd2['y'] + axd2['z']            
        dt2 = self.params.get('distance_threshold', self.default_distance_threshold) ** 2
        cross_recurrence = d2 <= dt2
        #np.save(self.export_filename(), cross_recurrence)
        #np.save(self.export_filename('block_action_filename'), badf)

        if self.params.get("plot_filename"):
            date_format = mdates.DateFormatter('%H:%M')
            #fig = plt.figure(figsize=(8, 8), constrained_layout=True)
            #spec = fig.add_gridspec(2, 2, width_ratios=[5, 1], height_ratios=[1,5])
            #axcr = fig.add_subplot(spec[1, 0])
            #axtop = fig.add_subplot(spec[0, 0], sharex=axcr)
            #axright = fig.add_subplot(spec[1, 1], sharey=axcr)

            fig, axcr = plt.subplots()

            time_bounds = [lgdf.index[0].to_pydatetime(), lgdf.index[-1].to_pydatetime()]
            #time_bounds = [badf.index[0].to_pydatetime(), badf.index[-1].to_pydatetime()] 
            extent = mdates.date2num(time_bounds * 2)

            #axtop.plot(badf.index, badf[player0])
            #axtop.axes.get_xaxis().set_visible(False)
            #axtop.set_xlim(time_bounds)
            #axright.plot(badf[player1], badf.index)
            #axright.axes.get_yaxis().set_visible(False)

            axcr.imshow(
                cross_recurrence, 
                origin="lower", 
                extent=extent, 
                cmap='Greys', 
                vmin=0, 
                vmax=1,
            )
            axcr.xaxis_date()
            axcr.yaxis_date()
            axcr.xaxis.set_major_formatter(date_format)
            axcr.yaxis.set_major_formatter(date_format)
            axcr.set_xlabel(player_label0)
            axcr.set_ylabel(player_label1)

            #_, max0 = axtop.get_ylim()
            #_, max1 = axright.get_xlim()
            #axtop.set_ylim([0, max(max0, max1)])
            #axright.set_xlim([0, max(max0, max1)])

            if self.params.get("plot_title"):
                plt.suptitle(self.params.get("plot_title"))
            fig.savefig(self.export_filename("plot_filename"))

    def get_block_action_df(self, df):
        "Returns a df filtered to include only block action"
        badf = df[df.event.isin(['BlockBreakEvent', 'BlockPlaceEvent'])]
        badf = self.trim_df(badf).copy(deep=True)
        players = badf.player.unique()
        for player in players:
            badf[player] = (badf.player == player).astype(bool)
        return badf[players].resample(self.params.get("granularity", self.default_granularity)).sum()


