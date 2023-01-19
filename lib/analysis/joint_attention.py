from pathlib import Path
import pandas as pd
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt
from analysis.base import BaseModel
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy.stats import ttest_ind

class JointAttentionCollaborationModel(BaseModel):
    """Computes Schneider, et al's (2016) collaboration metric.
    
     - When measure: pairwise then in groups larger than two
       each dyad is considered separately. 
     - When measure: group then in groups larger than two, JVA is counted
       whenever any dyad had JVA. 
     - When measure: player then each individual is considered; counting 
       JVA when they have JVA with any other group member.
        
    """
    expected_params = [
        'model',
        'export_dir',
        'group_names',
        'measure',
    ]
    optional_params = [
        'score_threshold',
    ]
    collaboration_assessment_file = "data/collaboration_assessment/collaboration_assessment.csv"
    export_base_name = "jva_collaboration"

    def validate(self):
        "Also ensure param measure is valid"
        errors = super().validate()
        measure = self.params.get("measure")
        if measure and measure not in ["pairwise", "group", "player"]:
            errors.append("Param 'measure' must be one of: pairwise, group, player")
        return errors

    def export(self):
        scores = self.get_collaboration_assessment_scores()
        data = []
        categorical = self.params.get('score_threshold') is not None
        for group in self.params['group_names']:
            jva = self.get_jva_df(group)
            players, pairwise_cols, player_cols = self.get_player_cols(jva)
            score = scores.loc[group].mean()
            if categorical:
                score = 'high' if score >= self.params['score_threshold'] else 'low'

            if self.params['measure'] == "pairwise":
                for col in pairwise_cols:
                    data.append({
                        "group": group,
                        "group_size": len(players),
                        "collaboration_score": score,
                        "percentage_jva": jva[col].mean(),
                    })
            elif self.params['measure'] == "group":
                data.append({
                    "group": group,
                    "group_size": len(players),
                    "collaboration_score": score,
                    "percentage_jva": jva[pairwise_jva_cols].any(axis=1).mean(),
                })
            elif self.params['measure'] == "player":
                for player, cols in player_cols.items():
                    data.append({
                        "group": group,
                        "group_size": len(players),
                        "collaboration_score": score,
                        "percentage_jva": jva[cols].any(axis=1).mean(),
                    })

        df = pd.DataFrame.from_records(data)
        df.to_csv(self.export_dir() / (self.export_base_name + ".csv"))

        if categorical:
            bp = sns.barplot(x="collaboration_score", y="percentage_jva", data=df)
            plt.xlabel("Collaboration level")
            plt.ylabel("Percentage of segment spent in JVA")
            bp.figure.savefig(self.export_dir() / (self.export_base_name + ".png"))
            test = ttest_ind(
                df[df.collaboration_score == "low"].percentage_jva,
                df[df.collaboration_score == "high"].percentage_jva,
                alternative="less",
                equal_var=False,
            )
        else:
            lm = sns.lmplot(x="percentage_jva", y="collaboration_score", data=df)
            ax = lm.axes[0, 0]
            ax.set_ylim([-0.5, 5.5])
            ax.figure.savefig(self.export_dir() / (self.export_base_name + ".png"))
            X = df.percentage_jva.to_numpy().reshape((-1, 1))
            y = df.collaboration_score.to_numpy()
            print(sm.OLS(y, X).fit().summary())

        plt.clf()
        vp = sns.violinplot(data=df, x="group_size", y="percentage_jva")
        vp.get_figure().savefig(self.export_dir() / (self.export_base_name + "_group_size.png"))

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
        return pd.read_csv(f)
        


