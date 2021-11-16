from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from analysis.base import BaseModel
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

class JointAttentionCollaborationModel(BaseModel):
    """
        Computes Schneider, et al's (2016) collaboration metric, considering 
        triads pairwise.
    """
    expected_params = [
        'model',
        'export_dir',
        'group_names',
    ]
    collaboration_assessment_file = "data/collaboration_assessment/collaboration_assessment.csv"
    export_base_name = "jva_collaboration"

    def export(self):
        scores = self.get_collaboration_assessment_scores()
        data = []
        for group in self.params['group_names']:
            score = scores.loc[group].mean()
            jva = self.get_jva_df(group)

            # Pairwise JVA has column names like "X-Y"
            pairwise_jva_cols = [col for col in jva.columns if '-' in col]
            if len(pairwise_jva_cols) == 3:
                group_size = 3
            elif len(pairwise_jva_cols) == 1:
                group_size = 2
            else:
                raise ValueError("Group size larger than 3 not supported")
            
            for col in [col for col in jva.columns if '-' in col]:
                data.append({
                    "group": group,
                    "group_size": group_size,
                    "collaboration_score": score,
                    "percentage_jva": jva[col].mean(),
                })
        df = pd.DataFrame.from_records(data, index="group")
        df.to_csv(self.export_dir() / (self.export_base_name + ".csv"))

        lm = sns.lmplot(x="percentage_jva", y="collaboration_score", hue="group_size", data=df)
        ax = lm.axes[0, 0]
        ax.set_ylim([-0.5, 5.5])
        ax.figure.savefig(self.export_dir() / (self.export_base_name + ".png"))

        plt.clf()

        vp = sns.violinplot(data=df, x="group_size", y="percentage_jva")
        vp.get_figure().savefig(self.export_dir() / (self.export_base_name + "_group_size.png"))

        X = df.percentage_jva.to_numpy().reshape((-1, 1))
        y = df.collaboration_score.to_numpy()
        print(sm.OLS(y, X).fit().summary())

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
        


