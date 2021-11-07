from invoke import task
from pathlib import Path
import code
import sys
import yaml
import pandas as pd
import numpy as np

sys.path.append("lib")

from lib.logs.reader import LogReader
from lib.segment import Segment
from lib.metadata import get_metadata_df

@task(help={
    "world": "name of world",
    "minecraft_username": "optional: sync one user's data",
    "dataframe": "whether to also generate a dataframe",
    "interact": "enter interactive mode to explore the resulting dataframe",
})
def sync(c, world, minecraft_username=None, dataframe=True, interact=False):
    "Sync logs from the server to local filesystem"
    remote_path = Path(c.minecraft_server.mscs_dir) / "worlds" / world / "plugins" / "SuperLog" / "logs"
    local_path = Path(c.local.logs_path) / world
    if minecraft_username:
        remote_path = remote_path / "players" / minecraft_username
        local_path = local_path / "players" / minecraft_username
    local_path.mkdir(exist_ok=True, parents=True)
    command = "rsync -r {}@{}:{} {} --delete".format(
        c.minecraft_server.username,
        c.minecraft_server.url,
        remote_path, 
        local_path
    )
    c.run(command)

    if minecraft_username:
        df_fn = world + "_" + minecraft_username + ".csv"
    else:
        df_fn = world + ".csv"
    df_path = Path(c.local.dataframe_path) / df_fn
    df_path.parent.mkdir(exist_ok=True, parents=True)
    df = LogReader(local_path).to_df()
    if dataframe:
        df.to_csv(df_path)
    if interact:
        print("Synced dataframe is bound to `df`")
        code.interact(local=locals())

@task(help={
    "world": "name of world",
    "minecraft_username": "optional: sync one user's data",
})
def interact(c, world, minecraft_username=None):
    "Drop into interactive console with the selected dataframe loaded"
    if minecraft_username:
        df_fn = world + "_" + minecraft_username + ".csv"
    else:
        df_fn = world + ".csv"
    df_path = Path(c.local.dataframe_path) / df_fn
    df = pd.read_csv(Path(c.local.dataframe_path) / df_fn,
            index_col="timestamp", parse_dates=["timestamp"])
    print("Synced dataframe is bound to `df`")
    code.interact(local=locals())

@task
def export_segment(c, params_file, dryrun=False):
    "Export a segment as speficied by a params file"
    pf = Path(params_file)
    if not pf.exists():
        raise ValueError("{} does not exist".format(pf))
    params = yaml.safe_load(pf.read_text())
    segment = Segment(yaml.safe_load())
    segment.validate()
    segment.export()

@task
def manifest(c, time=None, interact=False):
    "List and filter media assets"
    if time:
        time = np.datetime64(time)
    df = get_metadata_df(c.local.data_path, time=time)
    pd.options.display.max_colwidth = 100
    print(df.fillna("").sort_values("start"))
    if interact:
        print("Synced dataframe is bound to `df`")
        code.interact(local=locals())
    



