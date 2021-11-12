from segment.product.logs import SegmentLogs
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class SegmentTrace(SegmentLogs):
    """Produces a heatmap of character locations
    """
    optional_params = [
        "use_cache",
        "plot_filename",
        "players",
        "granularity",
        "alpha",
        "size",
        "palette",
        "diachronic"
    ]
    default_granularity = "1s"
    default_alpha = 0.1
    default_size=50
    default_diachronic_palette="flare"
    default_heatmap_palette="hls"

    def export(self):
        df = self.get_segment_data()
        df = df[["player", "location_x", "location_z"]]
        if self.params.get("players"):
            df = df[df.player.isin(self.params['players'])]
        granularity = self.params.get("granularity", self.default_granularity)
        df = df.resample(granularity).first().dropna()
        df.to_csv(self.export_filename())
        if self.params.get('plot_filename'):
            sns.set_theme(style="white")
            if self.params.get("diachronic"):
                self.plot_diachronic(df)
            else:
                self.plot_heatmap(df)
            plt.savefig(self.export_filename('plot_filename'), bbox_inches="tight")
        
    def plot_diachronic(self, df):
        df = df.reset_index()
        palette = self.params.get("palette", self.default_diachronic_palette)
        ax = sns.relplot(
            data=df,
            col="player",
            hue="timestamp",
            x="location_x",
            y="location_z",
            alpha=self.params.get("alpha", self.default_alpha),
            edgecolor=None,
            legend=False,
            palette=palette,
            s=self.params.get("size", self.default_size),
        )
        norm = plt.Normalize(df.timestamp.min().value, df.timestamp.max().value)
        sm = plt.cm.ScalarMappable(cmap=palette, norm=norm)
        sm.set_array([df.index.min(), df.index.max()])
        cbar = ax.figure.colorbar(sm)
        cbar.ax.set_yticklabels(pd.to_datetime(cbar.get_ticks()).strftime(date_format='%H:%M'))
            
    def plot_heatmap(self, df):
        return sns.relplot(
            data=df,
            hue="player",
            x="location_x",
            y="location_z",
            alpha=self.params.get("alpha", self.default_alpha),
            palette=self.params.get("palette", self.default_heatmap_palette),
            edgecolor=None,
            s=self.params.get("size", self.default_size),
        )
