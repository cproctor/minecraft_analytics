from invoke import task
from pathlib import Path
import code
import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

sys.path.append("lib")

from logs.reader import LogReader
from segment import Segment
from metadata import (
    get_metadata_df, 
    get_media_metadata, 
    METADATA_SUFFIX, 
    ts2s,
)
from analysis import MODELS

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
    df = pd.read_csv(
        Path(c.local.dataframe_path) / df_fn,
        index_col="timestamp", 
        parse_dates=["timestamp"],
        date_parser=lambda x: pd.to_datetime(x, utc=True),
    )
    print("Synced dataframe is bound to `df`")
    code.interact(local=locals())

@task
def export_segment(c, params_file, clean=False, dryrun=False):
    "Export a segment as speficied by a params file"
    pf = Path(params_file)
    if not pf.exists():
        raise ValueError("{} does not exist".format(pf))
    params = yaml.safe_load(pf.read_text())
    segment = Segment(params)
    segment.validate()
    segment.export(clean=clean)

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

@task
def localize(c, time, media_path, duration=None, end=None, reverse=False):
    """Convert a UTC timestamp to relative local time within a media path. 
    """
    if duration and end:
        raise ValueError("Must not specify duration and end")

    mp = Path(media_path)
    mp = mp.parent / (mp.name + METADATA_SUFFIX)
    md = get_media_metadata(mp)

    media_start_utc = pd.to_datetime(md['start']).to_pydatetime()
    if reverse:
        segment_start_media = timedelta(seconds=ts2s(time))
        segment_start_utc = media_start_utc + segment_start_media
    else:
        segment_start_utc = pd.to_datetime(time).to_pydatetime()
        segment_start_media = segment_start_utc - media_start_utc
    if duration:
        if duration.isdigit():
            duration = timedelta(seconds=int(duration))
        else:
            duration = timedelta(seconds=ts2s(duration))
        segment_end_utc = segment_start_utc + duration
        segment_end_media = segment_start_media + duration
    elif end:
        if reverse:
            segment_end_media = timedelta(seconds=ts2s(end))
            segment_end_utc = media_start_utc + segment_end_media
        else:
            segment_end_utc = pd.to_datetime(end).to_pydatetime()
            segment_end_media = segment_end_utc - media_start_utc
        duration = segment_end_utc - segment_start_utc
    else:
        duration = None
        end = None
    
    if reverse and duration:
        print(f"{segment_start_utc} - {segment_end_utc} ({duration})")
    elif reverse:
        print(f"{segment_start_utc}")
    elif duration:
        print(f"{segment_start_media} - {segment_end_media} ({duration})")
    else:
        print(f"{segment_start_media}")

@task
def analysis(c, params_file, clean=False):
    "Compute named analysis"
    pf = Path(params_file)
    if not pf.exists():
        raise ValueError("{} does not exist".format(pf))
    params = yaml.safe_load(pf.read_text())
    try:
        Model = MODELS[params['model']]
    except KeyError:
        raise ValueError("Model {} not found.".format(params['model']))
    model = Model(params)
    model.validate()
    model.prepare_export_dir(clean=clean)
    model.export()
    

