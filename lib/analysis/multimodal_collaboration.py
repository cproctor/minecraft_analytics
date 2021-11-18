# Multimodal Collaboration
# 1. Gather all joint visual attention DFs
# 2. Plot as bar graph with error bars.
# 3. See whether the difference is greater.

from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt
from analysis.base import BaseModel
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy.stats import ttest_ind

class MultimodalCollaborationModel(BaseModel):
    """Computes Schneider, et al's (2016) collaboration metric.
    
    Does JVA organize building activity? 
    Is the difference between JVA and non-JVA greater for high-collaboration groups than
    for low-collaboration groups?
        
    """
    expected_params = [
        'model',
        'export_dir',
        'group_names',
        'score_threshold',
    ]
    optional_params = [
        'granularity'
    ]
    default_granularity = '1s'
    collaboration_assessment_file = "data/collaboration_assessment/collaboration_assessment.csv"
    export_base_name = "jva_collaboration"

    def export(self):
        g = self.params.get('granularity', self.default_granularity)
        scores = self.get_collaboration_assessment_scores()
        dfs = []
        for group in self.params['group_names']:
            jva = self.get_jva_df(group)
            ba = self.get_ba_df(group).resample(g).sum()
            score = "high" if scores.loc[group].mean() >= self.params['score_threshold'] else "low"
            players, pairwise_cols, player_cols = self.get_player_cols(jva)
            for player, cols in player_cols.items():
                playerdata = jva[cols].any(axis=1).to_frame("jva").resample(g).agg({
                    "jva": (lambda sample: sample.any())
                })
                playerdata["player"] = player
                playerdata["group"] = group
                playerdata["group_size"] = len(players)
                playerdata["collaboration_score"] = score
                if player not in ba.columns:
                    ba[player] = 0
                playerdata = playerdata.merge(
                    ba[player].to_frame("block_actions"),
                    how="left",
                    left_index=True,
                    right_index=True,
                )
                dfs.append(playerdata)
        df = pd.concat(dfs)
        df.to_csv(self.export_dir() / (self.export_base_name + ".csv"))

        bp = sns.barplot(x="collaboration_score", hue="jva", y="block_actions", data=df)
        bp.figure.savefig(self.export_dir() / (self.export_base_name + ".png"))

        high_delta = self.mean_block_actions(df, "high", True) - self.mean_block_actions(df, "high", False)
        low_delta = self.mean_block_actions(df, "low", True) - self.mean_block_actions(df, "low", False)
        test = ttest_ind(
            high_delta,
            low_delta,
            equal_var=False,
        )
        print(test)

    def get_player_cols(self, jva):
        """Returns (players, pairwise_cols, player_cols) from JVA df
        Pairwise JVA has column names like "X-Y"
        players is like [a, b, c]
        pairwise_cols is like [a-b, a-c, b-c]
        player_cols is like {a: [a-b, a-c], b: [a-b, b-c], c: [a-c, b-c]}
        """
        pairwise_cols = [col for col in jva.columns if '-' in col]
        players = set(sum([col.split('-') for col in pairwise_cols], []))
        player_cols = defaultdict(list)
        for col in pairwise_cols:
            for player in col.split('-'):
                player_cols[player].append(col)
        return players, pairwise_cols, player_cols

    def get_collaboration_assessment_scores(self):
        "Loads scores df, averages assessor scores for each group, and returns"
        df = pd.read_csv(self.collaboration_assessment_file)
        df = df.drop(columns=["assessor"]).groupby("group").mean()
        return df

    def get_jva_df(self, group):
        "gets the JVA df for a group"
        workshop_num = group[1]
        f = Path("data/segments") / f"workshop_{workshop_num}_collaboration" / f"{group}_joint_attention.csv"
        return pd.read_csv(f, index_col="timestamp", parse_dates=["timestamp"])

    def get_ba_df(self, group):
        "Gets the block activity dataframe for a group"
        workshop_num = group[1]
        f = Path("data/segments") / f"workshop_{workshop_num}_collaboration" / f"{group}_block_activity.csv"
        return pd.read_csv(f, index_col="timestamp", parse_dates=["timestamp"])
        
    def mean_block_actions(self, df, score, jva):
        selection = df[(df.collaboration_score == score) & (df.jva == jva)]
        return selection.groupby(["group", "player"]).block_actions.mean()
        


